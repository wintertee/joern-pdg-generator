import asyncio
import glob
import os
import time

import aiofiles  # 用于异步文件操作
import openai
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

# 全局进度条实例，用于所有输出
pbar = None

load_dotenv()

# --- 1. 配置 ---

# 在这里手动设置您想要的并发请求数量
MAX_CONCURRENCY = 100

# 设置 API 请求失败后的最大重试次数
MAX_RETRIES = 5

# 连续错误触发panic退出的阈值
CONSECUTIVE_ERROR_THRESHOLD = 10

# 定义数据路径
DATA_PATH = "data/problem_descriptions"
OUTPUT_PATH = "data/specs"

# --- 2. 初始化 ---

# 直接使用真实的 OpenAI 客户端
# 代码会从环境变量 "OPENAI_API_KEY" 中自动读取密钥
try:
    client = openai.AsyncOpenAI()
except openai.OpenAIError as e:
    print("OpenAI 客户端初始化失败。")
    print("请确保您已将 OPENAI_API_KEY 设置为环境变量。")
    print(f"错误详情: {e}")
    exit()


# 创建一个固定大小的信号量（Semaphore）
semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

# 连续错误计数器
consecutive_errors = 0
error_lock = asyncio.Lock()  # 用于保护连续错误计数器的锁


# --- 3. 您的数据处理函数 ---


def build_message(content):
    """根据文件内容构建 OpenAI API 的 message。"""
    return [
        {
            "role": "user",
            "content": f'Provide a concise, one-sentence summary of the following programming problem. Describe its primary purpose and functional description, abstracting away any irrelevant thematic details and without including inputs and outputs or generating code blocks. For example, a good specification for a problem about "given a list of values, prints values greater than a threshold after doubling them" is: "The function iterates through a vector of integers, doubling and printing any value that exceeds a given threshold."\n\nProblem Description:\n```html\n{content}\n```',
        }
    ]


def tqdm_print(message):
    """使用tqdm兼容的方式打印消息，避免干扰进度条"""
    if pbar:
        pbar.write(message)
    else:
        print(message)


async def increment_consecutive_errors():
    """增加连续错误计数器，如果达到阈值则退出程序"""
    global consecutive_errors
    async with error_lock:
        consecutive_errors += 1
        tqdm_print(f"[{time.strftime('%H:%M:%S')}] ⚠️ 连续错误计数: {consecutive_errors}/{CONSECUTIVE_ERROR_THRESHOLD}")

        if consecutive_errors >= CONSECUTIVE_ERROR_THRESHOLD:
            tqdm_print(
                f"[{time.strftime('%H:%M:%S')}] 💥 PANIC: 连续错误已达到阈值 {CONSECUTIVE_ERROR_THRESHOLD}，程序退出！"
            )
            tqdm_print("这可能表明存在严重的系统问题，请检查网络连接、API密钥或其他配置。")
            os._exit(1)  # 强制退出程序


async def reset_consecutive_errors():
    """重置连续错误计数器"""
    global consecutive_errors
    async with error_lock:
        if consecutive_errors > 0:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] ✅ 重置连续错误计数器 (之前: {consecutive_errors})")
            consecutive_errors = 0


# --- 4. 核心 API 调用与文件保存函数 ---


async def process_and_save_file(input_path: str):
    """
    读取文件、调用API、处理重试，并在成功后立即保存结果。
    """
    global consecutive_errors

    # 从完整路径中提取文件名，例如 "problem1.html"
    base_filename = os.path.basename(input_path)
    # 构造输出文件名，例如 "problem1.txt"
    output_filename = os.path.splitext(base_filename)[0] + ".txt"
    output_filepath = os.path.join(OUTPUT_PATH, output_filename)

    # 如果输出文件已存在，直接跳过
    if os.path.exists(output_filepath):
        tqdm_print(f"[{time.strftime('%H:%M:%S')}] 🟡 跳过: {output_filename} (文件已存在)")
        return output_filepath  # 返回路径表示任务已处理

    # 读取文件内容
    try:
        async with aiofiles.open(input_path, "r", encoding="utf-8") as file:
            content = await file.read()
    except Exception as e:
        tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ 读取文件失败: {input_path}. 错误: {e}")
        await increment_consecutive_errors()
        return None

    # 构建 API 消息
    messages = build_message(content)

    # 重试循环
    for attempt in range(MAX_RETRIES):
        try:
            # 在信号量的上下文中执行 API 调用
            async with semaphore:
                tqdm_print(
                    f"[{time.strftime('%H:%M:%S')}] 🚀 开始请求: {base_filename} (并发数: {MAX_CONCURRENCY - semaphore._value}/{MAX_CONCURRENCY})"
                )

                response = await client.chat.completions.create(
                    model="deepseek-v3-241226",  # 您也可以选择 "gpt-4-turbo" 或 "gpt-3.5-turbo"
                    messages=messages,  # type: ignore
                )
                result_content = response.choices[0].message.content

            # --- 成功后，立刻异步写入文件 ---
            if result_content:
                async with aiofiles.open(output_filepath, "w", encoding="utf-8") as f:
                    await f.write(result_content.strip())  # 使用 .strip() 清理可能的前后空白
                tqdm_print(f"[{time.strftime('%H:%M:%S')}] ✅ 成功并保存: {output_filename}")

                # 成功时重置连续错误计数器
                await reset_consecutive_errors()
                return output_filepath  # 成功后返回输出路径
            else:
                tqdm_print(f"[{time.strftime('%H:%M:%S')}] ⚠️ API返回空内容: {base_filename}")
                await increment_consecutive_errors()
                return None

        except openai.RateLimitError:
            wait_time = 2 ** (attempt + 1)
            tqdm_print(
                f"[{time.strftime('%H:%M:%S')}] ⚠️ 速率限制: {base_filename}. 第 {attempt + 1} 次重试，等待 {wait_time}s..."
            )
            await asyncio.sleep(wait_time)

        except Exception as e:
            tqdm_print(f"[{time.strftime('%H:%M:%S')}] ❌ API未知错误: {base_filename}. 错误: {e}")
            # 对于其他类型的错误，可以选择中断重试
            await increment_consecutive_errors()
            return None

    tqdm_print(f"[{time.strftime('%H:%M:%S')}] 💀 任务最终失败: {base_filename} (已达最大重试次数)")
    await increment_consecutive_errors()
    return None


# --- 5. 主程序 ---


async def main():
    """
    主函数，发现文件、创建并并发运行所有任务。
    """
    global pbar

    # 确保输出目录存在
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # 获取所有 problem description 文件
    files = glob.glob(os.path.join(DATA_PATH, "*.html"))
    if not files:
        print(f"错误：在 '{DATA_PATH}' 目录下没有找到任何 .html 文件。")
        return

    # 为每个文件创建一个异步任务
    tasks = [process_and_save_file(file_path) for file_path in files]

    print(f"发现 {len(files)} 个文件。开始处理...")
    print(f"最大并发数设置为: {MAX_CONCURRENCY}")
    print(f"连续错误退出阈值: {CONSECUTIVE_ERROR_THRESHOLD}")
    start_time = time.time()

    # 使用 tqdm 进度条并发运行所有任务
    results = await tqdm.gather(*tasks, desc="处理文件", unit="file")

    end_time = time.time()

    success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
    failure_count = len(results) - success_count

    print("\n--- 任务完成 ---")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"成功任务数: {success_count}")
    print(f"失败任务数: {failure_count}")
    print(f"最终连续错误计数: {consecutive_errors}")


if __name__ == "__main__":
    # 运行前请确保：
    # 1. 已安装所需库: pip install openai aiofiles python-dotenv tqdm
    # 2. 已将 OpenAI API 密钥设置为名为 OPENAI_API_KEY 的环境变量
    # 3. 'data/problem_descriptions' 目录下有 .html 文件
    #
    # 新功能：
    # - 连续错误保护：程序会跟踪连续失败的任务数量，当连续错误达到阈值时panic退出
    # - 进度条显示：使用tqdm显示实时处理进度
    # - 文件存在检查：跳过已处理的文件，避免重复工作
    # - 智能错误处理：只在API返回有效内容时才创建文件，避免创建空文件
    asyncio.run(main())
