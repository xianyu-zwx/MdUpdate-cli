"""
文件操作工具函数
"""

import os
import shutil
from pathlib import Path


def read_input_content(input_path: str) -> str:
    """读取输入文件内容"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def create_backup(original_path: str, backup_path: str) -> None:
    """创建文件备份"""
    if os.path.exists(original_path):
        # 确保备份目录存在
        ensure_directory_exists(backup_path)
        shutil.copy2(original_path, backup_path)


def is_text_file(file_path: str) -> bool:
    """判断是否为文本文件"""
    return Path(file_path).suffix.lower() in ['.txt', '.md', '.markdown', '.text']


def ensure_directory_exists(file_path: str) -> None:
    """确保文件所在目录存在"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def setup_default_directories() -> None:
    """设置默认目录结构"""
    directories = [
        'docs/target',
        'docs/inputs',
        'example/input_samples'
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"创建目录: {directory}")


def copy_example_files() -> None:
    """复制示例文件到新目录结构"""
    # 如果example目录有文件但docs目录为空，复制文件
    example_target = "example/Linux & Devops面试题复习资料.md"
    docs_target = "docs/target/Linux & Devops面试题复习资料.md"

    example_input = "example/input_samples/Terraform面试题目.md"
    docs_input = "docs/inputs/Terraform面试题目.md"

    # 复制目标文档
    if os.path.exists(example_target) and not os.path.exists(docs_target):
        ensure_directory_exists(docs_target)
        shutil.copy2(example_target, docs_target)
        print(f"复制目标文档: {example_target} -> {docs_target}")

    # 复制输入文档
    if os.path.exists(example_input) and not os.path.exists(docs_input):
        ensure_directory_exists(docs_input)
        shutil.copy2(example_input, docs_input)
        print(f"复制输入文档: {example_input} -> {docs_input}")