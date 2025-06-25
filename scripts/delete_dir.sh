#!/bin/bash

# --- 递归删除所有名为 'spec' 的文件夹 ---
#
# 使用方法:
#   ./delete_spec_folders.sh /path/to/your/directory
#
# 说明:
#   这个脚本会从指定的父目录下递归地查找所有名为 'spec' 的文件夹，
#   然后将它们及其所有内容一并删除。
#   -print 选项会在删除前打印出将要被删除的目录，方便确认和记录。
#   -delete 选项是 find 命令内置的高效删除操作。

# 检查是否提供了目录参数
if [ -z "$1" ]; then
  echo "错误：请输入一个目标文件夹路径。"
  echo "用法: $0 /path/to/directory"
  exit 1
fi

# 检查提供的路径是否存在且是一个目录
if [ ! -d "$1" ]; then
  echo "错误：路径 '$1' 不存在或不是一个有效的文件夹。"
  exit 1
fi

TARGET_DIR=$1

echo "将在 '$TARGET_DIR' 文件夹下查找并删除所有名为 'spec' 的文件夹..."
echo "--------------------------------------------------------"

# 使用 find 命令查找并删除
# -type d: 只查找目录
# -name "spec": 查找名字精确匹配 "spec" 的
# -print: 在标准输出打印找到的路径（可选，但建议保留以便查看）
# -delete: 删除找到的目录及其内容
find "$TARGET_DIR" -type f -path "*/specs/*.txt" -delete

echo "--------------------------------------------------------"
echo "操作完成。"