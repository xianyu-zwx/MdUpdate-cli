#!/usr/bin/env python3
"""
Linux & 云计算运维面试题文档自动整理工具
主程序入口
"""

import argparse
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.document_processor import DocumentProcessor
from utils.file_utils import read_input_content, setup_default_directories
from utils.content_cleaner import clean_markdown_content


def main():
    """主函数"""
    # 初始化目录结构
    setup_default_directories()

    parser = argparse.ArgumentParser(
        description='Linux & 云计算运维面试题文档自动整理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --target "docs/target/document.md" --input "docs/inputs/new_content.md"
  python main.py --target "example/document.md" --section 7 --input "example/input_samples/terraform.md"
        """
    )

    parser.add_argument('--target', type=str, required=True,
                        help='目标Markdown文档路径')
    parser.add_argument('--input', type=str,
                        help='输入文件路径（可选，优先于--content）')
    parser.add_argument('--section', type=str,
                        help='指定插入的部分编号（如1-7，不指定则自动识别）')
    parser.add_argument('--content', type=str,
                        help='直接提供的文本内容（若--input存在则忽略）')
    parser.add_argument('--dry-run', action='store_true',
                        help='试运行，不实际修改文件')

    args = parser.parse_args()

    try:
        # 初始化文档处理器
        processor = DocumentProcessor(args.target)

        # 获取输入内容
        content = get_input_content(args)
        if not content.strip():
            print("错误：输入内容为空")
            return 1

        # 清理和标准化内容
        content = clean_markdown_content(content)

        # 插入内容
        if args.dry_run:
            print("试运行模式：不会实际修改文件")
            processor.dry_run_insert(content, args.section)
        else:
            processor.insert_content(content, args.section)
            processor.save_document()

        return 0

    except Exception as e:
        print(f"程序执行失败：{str(e)}")
        return 1


def get_input_content(args):
    """获取输入内容"""
    if args.input:
        return read_input_content(args.input)
    elif args.content:
        return args.content
    else:
        return get_content_from_stdin()


def get_content_from_stdin():
    """从标准输入获取内容"""
    print("请输入要添加的面试题内容（输入完成后按Ctrl+D结束，Windows按Ctrl+Z）：")
    content_lines = []
    try:
        while True:
            line = input()
            content_lines.append(line)
    except EOFError:
        pass
    return '\n'.join(content_lines)


if __name__ == "__main__":
    sys.exit(main())