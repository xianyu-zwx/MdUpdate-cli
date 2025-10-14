"""
文档处理核心逻辑
负责文档的加载、解析、内容插入和保存
"""

import re
import os
from typing import List, Optional, Tuple
from models.document import Document, Section, Title
from core.title_normalizer import TitleNormalizer
from utils.file_utils import create_backup


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, target_file_path: str):
        self.target_file_path = target_file_path
        self.backup_file_path = f"{target_file_path}.backup"
        self.document = Document()
        self.title_normalizer = TitleNormalizer()
        self._load_document()

    def _load_document(self) -> None:
        """加载并解析文档"""
        if not os.path.exists(self.target_file_path):
            self._create_new_document()
        else:
            self._load_existing_document()

    def _create_new_document(self) -> None:
        """创建新文档"""
        initial_content = "# Linux & 云计算运维面试题复习资料\n\n[TOC]\n\n"
        self.document.load_from_content(initial_content)

        # 保存初始文档
        with open(self.target_file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

    def _load_existing_document(self) -> None:
        """加载现有文档"""
        with open(self.target_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        self.document.load_from_lines(content)
        create_backup(self.target_file_path, self.backup_file_path)

    def determine_section(self, content: str) -> Tuple[str, bool]:
        """根据内容确定插入的部分和是否为全新部分
        返回: (section_number, is_new_section)
        """
        return self.document.determine_target_section(content)

    def insert_content(self, content: str, section: Optional[str] = None) -> None:
        """插入内容到文档"""
        if not section:
            section, is_new_section = self.determine_section(content)
            print(f"自动识别插入部分：第{section}部分 ({'全新部分' if is_new_section else '融入现有部分'})")

        # 标准化内容格式
        normalized_content = self.title_normalizer.normalize_content(content, section)

        # 插入内容
        self.document.insert_content(normalized_content, section)

        print(f"成功插入内容到第{section}部分")

    def dry_run_insert(self, content: str, section: Optional[str] = None) -> None:
        """试运行插入（不实际修改）"""
        if not section:
            section, is_new_section = self.determine_section(content)
            print(f"自动识别插入部分：第{section}部分 ({'全新部分' if is_new_section else '融入现有部分'})")

        normalized_content = self.title_normalizer.normalize_content(content, section)
        print(f"试运行：将插入以下内容到第{section}部分")
        print("=" * 50)
        print(normalized_content)
        print("=" * 50)

    def save_document(self) -> None:
        """保存文档"""
        with open(self.target_file_path, 'w', encoding='utf-8') as f:
            f.writelines(self.document.get_content_lines())

        print(f"\n文档更新完成！")
        print(f"目标文件：{self.target_file_path}")
        print(f"备份文件：{self.backup_file_path}")