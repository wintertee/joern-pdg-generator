import argparse
import glob
import multiprocessing
import os
import subprocess

from tqdm import tqdm

# --- 配置 ---
# 要处理的语言
LANG = "cpp"
# 数据集的基础目录路径
BASE_DATA_PATH = "./data/Project_CodeNet_C++1000"
# 用于查找源文件的 Glob 模式 (原始 bash 脚本为: $path/*/*.$lang)
# 修改后：这意味着在 BASE_DATA_PATH 下有一级子目录包含源文件。
FILE_GLOB_PATTERN = os.path.join(BASE_DATA_PATH, "*", f"*.{LANG}")
# CPG-neo4j 可执行文件的绝对路径
CPG_NEO4J_EXECUTABLE = "../cpg/cpg-neo4j/build/install/cpg-neo4j/bin/cpg-neo4j"
# json2dot.py 脚本的绝对路径
JSON2DOT_SCRIPT = os.path.abspath("./src/json2dot.py")
# --- 配置结束 ---


def process_file(args):
    """
    使用 CPG-neo4j 和 json2dot.py 脚本处理单个源代码文件。
    每个文件的输出都存储在以输入文件命名的目录内的 'cpg' 子目录中，
    该目录与输入文件位于同一目录。
    例如：输入: path/to/file.cpp -> 输出: path/to/file/cpg/
    返回: (file_path, success_boolean, message_string)
    """
    file_path, lang_param = args
    abs_file_path = os.path.abspath(file_path)
    current_file_cpg_root = ""  # 为清晰起见，在早期错误发生时初始化

    try:
        # 1. 确定并为此文件创建唯一的输出目录。
        input_file_parent_dir = os.path.dirname(abs_file_path)
        input_filename_no_ext = os.path.splitext(os.path.basename(abs_file_path))[0]
        per_file_base_dir = os.path.join(input_file_parent_dir, input_filename_no_ext)
        current_file_cpg_root = os.path.join(per_file_base_dir, "cpg")
        os.makedirs(current_file_cpg_root, exist_ok=True)

        # 2. 运行 cpg-neo4j 生成 JSON 文件
        cpg_json_output = os.path.join(current_file_cpg_root, "cpg-export.json")
        cpg_cmd = [CPG_NEO4J_EXECUTABLE, "--export-json", cpg_json_output, "--no-neo4j", abs_file_path]
        cpg_result = subprocess.run(
            cpg_cmd,
            cwd=current_file_cpg_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if cpg_result.returncode != 0:
            print(f"\n[ERROR] cpg-neo4j 执行失败: {' '.join(cpg_cmd)}")
            print(f"[STDOUT]:\n{cpg_result.stdout}")
            print(f"[STDERR]:\n{cpg_result.stderr}")
            raise subprocess.CalledProcessError(
                returncode=cpg_result.returncode,
                cmd=cpg_cmd,
                stderr=cpg_result.stderr,
                output=cpg_result.stdout,
            )

        # 3. 运行 json2dot.py 生成 DOT 文件
        json2dot_cmd = ["uv", "run", JSON2DOT_SCRIPT, cpg_json_output, "-o", current_file_cpg_root]
        json2dot_result = subprocess.run(
            json2dot_cmd,
            cwd=current_file_cpg_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if json2dot_result.returncode != 0:
            print(f"\n[ERROR] json2dot.py 执行失败: {' '.join(json2dot_cmd)}")
            print(f"[STDOUT]:\n{json2dot_result.stdout}")
            print(f"[STDERR]:\n{json2dot_result.stderr}")
            raise subprocess.CalledProcessError(
                returncode=json2dot_result.returncode,
                cmd=json2dot_cmd,
                stderr=json2dot_result.stderr,
                output=json2dot_result.stdout,
            )

        return (file_path, True, f"输出位于 {current_file_cpg_root}")

    except subprocess.CalledProcessError as e:
        error_details = f"命令 '{' '.join(e.cmd)}' 执行失败，退出代码 {e.returncode}。"
        if hasattr(e, "output") and e.output and e.output.strip():
            error_details += f"\n标准输出:\n{e.output.strip()}"
        if e.stderr and e.stderr.strip():
            error_details += f"\n标准错误:\n{e.stderr.strip()}"
        return (file_path, False, error_details)
    except FileNotFoundError as e:
        return (file_path, False, f"未找到所需的文件或目录 - {e}")
    except Exception as e:
        return (file_path, False, f"发生意外错误 - {type(e).__name__}: {e}")


def main():
    """
    主函数，用于发现文件并并行处理它们。
    处理 KeyboardInterrupt 以实现优雅关闭。
    """
    parser = argparse.ArgumentParser(description="使用 CPG-neo4j 和 json2dot.py 并行处理源文件")
    parser.add_argument(
        "--num_workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="并行进程数，默认等于CPU核心数",
    )
    parser.add_argument(
        "--file_list",
        type=str,
        help="包含要处理的文件列表的文件路径。如果提供，则从此文件读取文件列表而不使用glob模式搜索",
    )
    args = parser.parse_args()

    print("--------------------------------------------------------------------------")
    print("🐍 使用 CPG-neo4j 和 json2dot.py 处理源文件的 Python 脚本")
    print("   (输出到每个文件的 '<文件名>/cpg/' 子目录)")
    print("--------------------------------------------------------------------------")
    print("📋 先决条件:")
    print("  1. CPG-neo4j 必须已安装并可执行。")
    if not args.file_list:
        print(f"  2. 数据集 (例如 Project_CodeNet_C++1000) 必须位于: {os.path.abspath(BASE_DATA_PATH)}")
    print(f"  {'3' if not args.file_list else '2'}. json2dot.py 脚本必须存在于: {JSON2DOT_SCRIPT}")
    if args.file_list:
        print("  3. 文件列表格式: 每行一个文件路径，支持 # 开头的注释行")
    print("随时按 Ctrl+C 中断处理。")
    print("--------------------------------------------------------------------------\n")

    if not os.path.exists(JSON2DOT_SCRIPT):
        print(f"🔴 严重错误: 未找到 json2dot.py 脚本 {JSON2DOT_SCRIPT}。正在退出。")
        return

    if not os.path.exists(CPG_NEO4J_EXECUTABLE):
        print(f"🔴 严重错误: 未找到 CPG-neo4j 可执行文件 {CPG_NEO4J_EXECUTABLE}。正在退出。")
        return

    # 根据是否提供文件列表选择不同的文件发现方式
    if args.file_list:
        # 从文件列表读取文件
        if not os.path.exists(args.file_list):
            print(f"🔴 严重错误: 指定的文件列表 {args.file_list} 不存在。正在退出。")
            return

        print(f"📂 从文件列表读取要处理的文件: {args.file_list}...")
        files_to_process = []
        try:
            with open(args.file_list, "r", encoding="utf-8") as f:
                for line in f:
                    file_path = line.strip()
                    if file_path and not file_path.startswith("#"):  # 跳过空行和注释行
                        if os.path.exists(file_path):
                            files_to_process.append(file_path)
                        else:
                            print(f"⚠️ 警告: 文件不存在，跳过: {file_path}")
        except Exception as e:
            print(f"🔴 严重错误: 无法读取文件列表 {args.file_list}: {e}")
            return

        files_to_process = sorted(files_to_process)
        print(f"📋 从文件列表中读取到 {len(files_to_process)} 个有效文件。")
    else:
        # 使用原有的glob模式搜索
        if not os.path.isdir(BASE_DATA_PATH):
            print(f"🔴 严重错误: 基础数据路径 {os.path.abspath(BASE_DATA_PATH)} 不存在或不是目录。正在退出。")
            return

        print(f"🔍 正在使用模式搜索 '{LANG}' 文件: {FILE_GLOB_PATTERN}...")
        # 按文件名排序文件列表
        files_to_process = sorted(glob.glob(FILE_GLOB_PATTERN))

    # 断点续跑数据库文件
    PROCESSED_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_files.txt")
    FAILED_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "failed_files.txt")
    processed_files_set = set()
    if os.path.exists(PROCESSED_DB_PATH):
        with open(PROCESSED_DB_PATH, "r", encoding="utf-8") as f:
            for line in f:
                processed_files_set.add(line.strip())

    # 过滤掉已处理的文件
    original_count = len(files_to_process)
    files_to_process = [fp for fp in files_to_process if os.path.abspath(fp) not in processed_files_set]
    filtered_count = original_count - len(files_to_process)

    if not files_to_process:
        if args.file_list:
            print("文件列表中的所有文件均已处理，无需重复处理。")
        else:
            print("所有文件均已处理，无需重复处理。")
        return

    if args.file_list:
        print(f"✅ 文件列表中有 {len(files_to_process)} 个文件需要处理")
        if filtered_count > 0:
            print(f"   (已跳过 {filtered_count} 个已处理的文件)")
    else:
        print(f"✅ 找到 {len(files_to_process)} 个要处理的文件 (已按文件名排序，已跳过已处理文件)。")
    print("ℹ️  每个文件 'path/to/file.ext' 的输出将位于 'path/to/file/cpg/'。")

    tasks_args = [
        (
            fp,
            LANG,
        )
        for fp in files_to_process
    ]
    num_workers = args.num_workers
    # num_workers = max(1, min(cpu_cores // 2, 16))
    # num_workers = 1 # 用于调试

    results_log = []  # 存储 (file_path, success_bool, message_str) 元组
    success_count = 0
    error_count = 0
    print(f"⚙️  正在使用 {num_workers} 个工作进程初始化并行处理...")

    try:
        with multiprocessing.Pool(processes=num_workers) as pool:
            with tqdm(total=len(tasks_args), desc="🚀 处理文件", smoothing=0) as pbar:
                for result_tuple in pool.imap_unordered(process_file, tasks_args):
                    results_log.append(result_tuple)
                    if result_tuple[1]:
                        success_count += 1
                    else:
                        error_count += 1
                    pbar.set_postfix({"成功": success_count, "失败": error_count})
                    pbar.update(1)

                    # Panic exit if error rate > 50% and processed > 10
                    total_processed = success_count + error_count
                    if total_processed > 10 and error_count / total_processed > 0.5:
                        print(
                            "\n🛑 Panic exit: 错误率超过50%，已处理文件数：{}，失败数：{}".format(
                                total_processed, error_count
                            )
                        )
                        pool.terminate()
                        pool.join()
                        raise SystemExit("Panic exit due to high error rate.")
    except KeyboardInterrupt:
        print("\n🚫 用户通过 (Ctrl+C) 中断了进程。工作进程正在终止。")
        print("   将显示已完成工作的摘要。")
    except Exception as e:
        print(f"\n❌ 并行处理期间发生意外错误: {type(e).__name__} - {e}")
        print("   工作进程正在终止。将显示已完成工作的摘要。")
    finally:
        # 统一写入本轮新成功的文件到 processed_files.txt
        new_success_files = [os.path.abspath(fp) for fp, success, _ in results_log if success]
        if new_success_files:
            with open(PROCESSED_DB_PATH, "a", encoding="utf-8") as f:
                for fp in new_success_files:
                    f.write(fp + "\n")

        # 统一写入本轮新失败的文件到 failed_files.txt
        new_failed_files = [os.path.abspath(fp) for fp, success, _ in results_log if not success]
        if new_failed_files:
            with open(FAILED_DB_PATH, "a", encoding="utf-8") as f:
                for fp in new_failed_files:
                    f.write(fp + "\n")

        print("\n--- 📊 处理摘要 ---")

        # 根据原始文件名对结果进行排序
        results_log.sort(key=lambda item: item[0])

        success_count = 0
        error_count = 0

        if not results_log and files_to_process:
            print("没有任务完成或记录结果，可能是由于早期中断或错误。")

        for original_fp, success, msg_detail in results_log:
            if success:
                success_count += 1
                # 可以选择在这里打印每个成功的文件的详细信息，如果需要的话
                # print(f"成功: {original_fp} 已处理。{msg_detail}")
            else:
                error_count += 1
                print(f"处理 {original_fp} 时出错: {msg_detail}")  # 打印失败文件的完整错误消息

        total_attempted_or_logged = len(results_log)
        print(f"\n处理/尝试的任务数（截至中断/完成）: {total_attempted_or_logged} / {len(files_to_process)}")
        print(f"成功处理: {success_count}")
        print(f"失败或出错: {error_count}")

        if error_count > 0:
            print("⚠️ 请查看上面的错误消息以获取有关失败文件的详细信息。")
        elif success_count > 0 and total_attempted_or_logged == len(files_to_process) and error_count == 0:
            print("✅ 所有文件均已成功处理！")
        elif success_count > 0:
            print("✅ 部分文件已成功处理。")
        elif total_attempted_or_logged == 0 and len(files_to_process) > 0:
            print("ℹ️ 没有文件被处理（可能是在处理开始前立即中断或设置问题）。")
        else:
            print("ℹ️ 处理运行完成。")

        print(f"🔗 已处理的文件记录保存在: {PROCESSED_DB_PATH}")
        if new_failed_files:
            print(f"❌ 失败的文件记录保存在: {FAILED_DB_PATH}")


if __name__ == "__main__":
    main()
