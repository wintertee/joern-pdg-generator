import asyncio
import glob
import os
import signal
import time
from dataclasses import dataclass

import aiofiles
import openai
from dotenv import load_dotenv
from prompt_generator import PromptGenerator
from tqdm import tqdm


@dataclass
class Task:
    """单个处理任务"""

    problem_id: str
    code_path: str
    spec_dir: str


# 全局任务队列和统计
task_queue = None  # 将在main函数中初始化
total_tasks = 0
completed_tasks = 0
failed_tasks = 0
task_lock = asyncio.Lock()

# 全局进度条实例，用于所有输出
pbar = None

load_dotenv()

# --- 1. 配置 ---

# 在这里手动设置您想要的并发请求数量
MAX_CONCURRENCY = 128

# 设置 API 请求失败后的最大重试次数
MAX_RETRIES = 5

# 定义数据路径 - 使用绝对路径确保路径正确
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_PATH = os.path.join(PROJECT_ROOT, "data/problem_descriptions")
CODE_ROOT = os.path.join(PROJECT_ROOT, "data/Project_CodeNet_C++1000")

# 添加更多配置选项
PROGRESS_SAVE_INTERVAL = 100  # 每处理100个任务保存一次进度

# --- 2. 初始化 ---

# 直接使用真实的 OpenAI 客户端
# 代码会从环境变量 "OPENAI_API_KEY" 中自动读取密钥
try:
    client = openai.AsyncOpenAI(
        timeout=60.0,  # 设置超时时间
        max_retries=0,  # 在应用层处理重试
    )
except openai.OpenAIError as e:
    print("OpenAI 客户端初始化失败。")
    print("请确保您已将 OPENAI_API_KEY 设置为环境变量。")
    print(f"错误详情: {e}")
    exit()


# 创建一个固定大小的信号量（Semaphore）
semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

# 全局标志用于优雅关闭
shutdown_flag = False
shutdown_event = asyncio.Event()


def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭程序"""
    global shutdown_flag, task_queue
    print("\n收到关闭信号，正在优雅关闭...")
    shutdown_flag = True

    # 立即清空任务队列
    if task_queue is not None:
        while not task_queue.empty():
            try:
                task_queue.get_nowait()
                task_queue.task_done()
            except asyncio.QueueEmpty:
                break
        print("已清空任务队列")

    # 设置事件通知所有等待的协程
    if shutdown_event:
        asyncio.create_task(set_shutdown_event())


async def set_shutdown_event():
    """异步设置关闭事件"""
    shutdown_event.set()


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# --- 3. 您的数据处理函数 ---


def tqdm_print(message):
    """使用tqdm兼容的方式打印消息，避免干扰进度条"""
    if pbar:
        pbar.write(message)
    else:
        print(message)


# --- 4. 核心 API 调用与文件保存函数 ---


async def process_single_task(task: Task) -> bool:
    """
    处理单个任务，返回是否成功
    """
    global shutdown_flag

    # 检查是否收到关闭信号
    if shutdown_flag:
        return False

    # 确保输出目录存在
    os.makedirs(task.spec_dir, exist_ok=True)

    # 读取problem description
    problem_desc_path = os.path.join(DATA_PATH, f"{task.problem_id}.html")
    try:
        async with aiofiles.open(problem_desc_path, "r", encoding="utf-8") as f:
            problem_description = await f.read()
    except Exception as e:
        tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ 读取problem description失败: {problem_desc_path}. 错误: {e}")
        return False

    # 读取code
    try:
        async with aiofiles.open(task.code_path, "r", encoding="utf-8") as f:
            code = await f.read()
    except Exception as e:
        tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ 读取code失败: {task.code_path}. 错误: {e}")
        return False

    prompt_gen = PromptGenerator(problem_description, "cpp", code)

    # 针对每个level生成并保存
    level_methods = [
        ("level_1.txt", prompt_gen.build_level_1_message),
        ("level_2.txt", prompt_gen.build_level_2_message),
        ("level_3.txt", prompt_gen.build_level_3_message),
        ("level_4.txt", prompt_gen.build_level_4_message),
        ("level_5.txt", prompt_gen.build_level_5_message),
        ("level_6.txt", prompt_gen.build_level_6_message),
        ("level_7.txt", prompt_gen.build_level_7_message),
    ]

    success_count = 0
    for filename, message_func in level_methods:
        # 检查是否收到关闭信号
        if shutdown_flag:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] 🛑 收到关闭信号，停止处理剩余level")
            break

        output_filepath = os.path.join(task.spec_dir, filename)
        if os.path.exists(output_filepath):
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] 🟡 跳过: {output_filepath} (文件已存在)")
            success_count += 1
            continue

        # 处理单个level
        if await process_single_level(output_filepath, message_func):
            success_count += 1
        else:
            # 如果任何一个level失败，不继续处理剩余的level
            break

    return success_count > 0


async def process_single_level(output_filepath: str, message_func) -> bool:
    """处理单个level的API调用"""
    messages = message_func()

    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                # 不输出开始请求的日志
                response = await client.chat.completions.create(
                    model="deepseek-v3-241226",
                    messages=messages,  # type: ignore
                )

                # 检查响应的完整性
                if not response.choices or len(response.choices) == 0:
                    tqdm_print(f"[{time.strftime('%H:%M:%S')}] ⚠️ API返回空choices: {output_filepath}")
                    return False

                result_content = response.choices[0].message.content

            if result_content:
                async with aiofiles.open(output_filepath, "w", encoding="utf-8") as f:
                    await f.write(result_content.strip())
                # 不输出成功保存的日志
                return True
            else:
                tqdm_print(f"[{time.strftime('%H:%M:%S')}] ⚠️ API返回空内容: {output_filepath}")
                return False

        except openai.RateLimitError:
            if attempt < MAX_RETRIES - 1:  # 如果不是最后一次重试
                wait_time = 2 ** (attempt + 1)
                tqdm_print(
                    f"[{time.strftime('%H:%M:%S')}] ⚠️ 速率限制: {output_filepath}. 第 {attempt + 1} 次重试，等待 {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
                continue  # 继续下一次重试
            else:
                tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ 速率限制重试次数耗尽: {output_filepath}")
                return False

        except openai.APIError as e:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ API错误: {output_filepath}. 错误: {e}")
            return False

        except Exception as e:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ 未知错误: {output_filepath}. 错误: {e}")
            return False

    tqdm_print(f"[{time.strftime('%H:%M:%S')}] 💀 任务最终失败: {output_filepath} (已达最大重试次数)")
    return False


async def validate_file_paths():
    """验证必要的文件路径是否存在"""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"问题描述目录不存在: {DATA_PATH}")
    if not os.path.exists(CODE_ROOT):
        raise FileNotFoundError(f"代码根目录不存在: {CODE_ROOT}")


async def update_task_stats(completed: bool = True):
    """更新任务统计"""
    global completed_tasks, failed_tasks
    async with task_lock:
        if completed:
            completed_tasks += 1
        else:
            failed_tasks += 1


# --- 5. 主程序 ---


async def main():
    """
    主函数，使用工作池模式处理任务
    """
    global pbar, task_queue, total_tasks, shutdown_flag

    # 验证文件路径
    try:
        await validate_file_paths()
    except Exception as e:
        print(f"初始化错误: {e}")
        return

    # 基本设置打印（保留）

    # 创建任务列表（只占用少量内存）
    try:
        task_list = await create_task_list()
        total_tasks = len(task_list)
    except Exception as e:
        print(f"创建任务列表失败: {e}")
        return

    if total_tasks == 0:
        print("没有找到需要处理的任务")
        return

    print(f"📋 发现 {total_tasks} 个代码文件")
    print(f"⚙️ 最大并发数设置为: {MAX_CONCURRENCY}")

    # 创建任务队列
    task_queue = asyncio.Queue()

    # 将任务添加到队列中
    # 启动消息（保留基本信息）
    for task in task_list:
        await task_queue.put(task)

    # 任务加载完成

    # 释放任务列表内存
    del task_list

    start_time = time.time()

    # 创建工作协程池
    workers = []
    for i in range(MAX_CONCURRENCY):
        worker_task = asyncio.create_task(worker(i))
        workers.append(worker_task)

    # 工作协程启动

    # 创建进度条并赋值给全局变量
    pbar = tqdm(total=total_tasks, desc="处理任务", unit="file", smoothing=0)

    try:
        # 等待所有任务完成或收到关闭信号
        last_progress = 0
        while True:
            if shutdown_flag:
                print("收到关闭信号，立即停止所有工作协程...")
                # 立即取消所有工作协程
                for worker_task in workers:
                    worker_task.cancel()
                break

            if task_queue.empty() and completed_tasks + failed_tasks >= total_tasks:
                # 所有任务完成
                break

            # 更新进度条
            current_progress = completed_tasks + failed_tasks
            if current_progress > last_progress:
                pbar.update(current_progress - last_progress)
                pbar.set_postfix(
                    {"成功": completed_tasks, "失败": failed_tasks, "剩余": task_queue.qsize() if task_queue else 0}
                )
                last_progress = current_progress

            await asyncio.sleep(1)  # 更频繁地更新进度条

    except KeyboardInterrupt:
        print("收到键盘中断信号，立即停止...")
        shutdown_flag = True
        # 立即取消所有工作协程
        for worker_task in workers:
            worker_task.cancel()

    finally:
        # 关闭进度条
        if "pbar" in locals():
            pbar.close()

        # 确保设置关闭标志
        shutdown_flag = True

        # 优雅关闭工作协程
        # 关闭协程（保留）
        for worker_task in workers:
            if not worker_task.cancelled():
                worker_task.cancel()

        # 等待所有工作协程完成，但不超过5秒
        try:
            await asyncio.wait_for(asyncio.gather(*workers, return_exceptions=True), timeout=5.0)
        except asyncio.TimeoutError:
            print("部分工作协程未能在5秒内正常退出")

        # 清空剩余队列
        if task_queue is not None:
            remaining_tasks = 0
            while not task_queue.empty():
                try:
                    task_queue.get_nowait()
                    task_queue.task_done()
                    remaining_tasks += 1
                except asyncio.QueueEmpty:
                    break
            if remaining_tasks > 0:
                print(f"清空了队列中剩余的 {remaining_tasks} 个任务")

        # 关闭进度条
        if pbar:
            pbar.close()

    end_time = time.time()

    print("\n--- 任务完成 ---")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"总任务数: {total_tasks}")
    print(f"成功任务数: {completed_tasks}")
    print(f"失败任务数: {failed_tasks}")
    if shutdown_flag:
        print("⚠️ 程序被用户中断")


async def worker(worker_id: int):
    """工作协程，从队列中获取任务并处理"""
    global task_queue

    while True:
        # 首先检查是否需要退出
        if shutdown_flag:
            # Worker收到关闭信号，静默退出
            break

        try:
            # 检查task_queue是否已初始化
            if task_queue is None:
                await asyncio.sleep(0.1)
                continue

            # 从队列获取任务，设置较短的超时
            task = await asyncio.wait_for(task_queue.get(), timeout=0.5)

            # 再次检查关闭信号（获取任务后立即检查）
            if shutdown_flag:
                # 将任务放回队列或直接标记完成
                task_queue.task_done()
                # Worker在处理前收到关闭信号，静默退出
                break

            # 不输出开始处理的日志

            # 处理任务
            success = await process_single_task(task)

            # 更新统计
            await update_task_stats(success)

            # 标记任务完成
            task_queue.task_done()

            # 不输出完成或失败的日志

        except asyncio.TimeoutError:
            # 超时，继续检查关闭标志
            continue
        except asyncio.CancelledError:
            # 协程被取消，静默退出
            break
        except Exception as e:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] 💥 Worker {worker_id} 异常: {e}")
            if task_queue:
                task_queue.task_done()
            await update_task_stats(False)

    # Worker退出（静默）


async def create_task_list() -> list[Task]:
    """创建任务列表，只存储路径信息"""
    # 获取所有.cpp文件，基于CODE_ROOT遍历
    cpp_files = glob.glob(os.path.join(CODE_ROOT, "*", "*.cpp"))
    if not cpp_files:
        raise FileNotFoundError(f"在 '{CODE_ROOT}' 目录下没有找到任何 .cpp 文件")

    tasks = []
    processed_problems = set()  # 追踪已处理的问题，避免重复检查

    for cpp_path in cpp_files:
        # 从文件路径提取问题ID：/path/to/CODE_ROOT/p00000/filename.cpp -> p00000
        problem_id = os.path.basename(os.path.dirname(cpp_path))

        # 检查对应的problem description是否存在
        problem_desc_path = os.path.join(DATA_PATH, f"{problem_id}.html")
        if not os.path.exists(problem_desc_path):
            if problem_id not in processed_problems:
                print(f"⚠️ 未找到问题描述文件: {problem_desc_path}")
                processed_problems.add(problem_id)
            continue

        # 构建spec目录路径，但不在这里创建目录
        code_dir = os.path.dirname(cpp_path)
        code_filename = os.path.splitext(os.path.basename(cpp_path))[0]  # 获取不含扩展名的文件名
        spec_dir = os.path.join(code_dir, code_filename, "specs")

        tasks.append(Task(problem_id=problem_id, code_path=cpp_path, spec_dir=spec_dir))

    return tasks


if __name__ == "__main__":
    # 运行前请确保：
    # 1. 已安装所需库: pip install openai aiofiles python-dotenv
    # 2. 已将 OpenAI API 密钥设置为名为 OPENAI_API_KEY 的环境变量
    # 3. 'data/problem_descriptions' 目录下有 .html 文件
    #
    # 功能：
    # - 工作池模式：使用固定数量的工作协程处理任务，控制内存使用
    # - 文件存在检查：跳过已处理的文件，避免重复工作
    # - 智能错误处理：只在API返回有效内容时才创建文件，避免创建空文件
    # - 优雅关闭：支持Ctrl+C中断并正确清理资源
    asyncio.run(main())
