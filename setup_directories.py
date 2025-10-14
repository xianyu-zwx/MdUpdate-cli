#!/usr/bin/env python3
"""
目录初始化脚本
"""

import os
import sys
from utils.file_utils import setup_default_directories, copy_example_files


def main():
    """初始化目录结构"""
    print("正在设置目录结构...")

    # 设置默认目录
    setup_default_directories()

    # 复制示例文件
    copy_example_files()

    print("目录设置完成！")
    print("\n推荐的文件位置：")
    print("目标文档: docs/target/Linux & Devops面试题复习资料.md")
    print("待添加文档: docs/inputs/")
    print("\n使用方法：")
    print('python main.py --target "docs/target/Linux & Devops面试题复习资料.md" --input "docs/inputs/你的文件.md"')


if __name__ == "__main__":
    main()