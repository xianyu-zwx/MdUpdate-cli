"""
标题标准化器
负责将不同格式的标题转换为统一格式
"""

import re
from typing import Dict, List, Tuple


class TitleNormalizer:
    """标题标准化器"""

    def __init__(self):
        # 中文数字映射
        self.chinese_numbers = {
            '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
            '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
        }

        # 标题模式
        self.title_patterns = {
            'chinese_section': re.compile(r'^([一二三四五六七八九十])、\s*(.*)$'),
            'numbered_section': re.compile(r'^#+\s+(\d+)\.\s*(.*)$'),
            'chinese_with_hash': re.compile(r'^#+\s+([一二三四五六七八九十])、\s*(.*)$')
        }

    def normalize_content(self, content: str, target_section: str) -> str:
        """标准化内容标题"""
        lines = content.split('\n')
        normalized_lines = []

        # 初始化计数器
        section_counter = 0
        subsection_counter = 0
        subsubsection_counter = 0

        for line in lines:
            normalized_line, counters = self._normalize_line(
                line, target_section,
                section_counter, subsection_counter, subsubsection_counter
            )

            # 更新计数器
            if counters:
                section_counter, subsection_counter, subsubsection_counter = counters

            normalized_lines.append(normalized_line)

        return '\n'.join(normalized_lines)

    def _normalize_line(self, line: str, target_section: str,
                       section_num: int, subsection_num: int, subsubsection_num: int) -> Tuple[str, Tuple]:
        """标准化单行标题
        返回: (normalized_line, (new_section_num, new_subsection_num, new_subsubsection_num))
        """
        stripped_line = line.strip()

        # 匹配纯中文数字标题（如：一、Terraform基础与核心概念）
        match = self.title_patterns['chinese_section'].match(stripped_line)
        if match:
            chinese_num = match.group(1)
            title_text = match.group(2)
            number = self.chinese_numbers.get(chinese_num, str(section_num + 1))
            new_section_num = section_num + 1
            return f"## {target_section}.{number} {title_text}", (new_section_num, 0, 0)

        # 匹配带#号的中文数字标题（如：### 一、Terraform基础与核心概念）
        match = self.title_patterns['chinese_with_hash'].match(stripped_line)
        if match:
            chinese_num = match.group(1)
            title_text = match.group(2)
            number = self.chinese_numbers.get(chinese_num, str(section_num + 1))
            new_section_num = section_num + 1
            return f"## {target_section}.{number} {title_text}", (new_section_num, 0, 0)

        # 匹配数字标题（如：#### 1. Terraform采用什么语言编写？）
        match = self.title_patterns['numbered_section'].match(stripped_line)
        if match:
            old_num = match.group(1)
            title_text = match.group(2)

            # 根据标题级别确定是子节还是子子节
            if stripped_line.startswith('### '):
                # 三级标题 -> 子节
                new_subsection_num = subsection_num + 1
                return f"### {target_section}.{section_num}.{new_subsection_num} {title_text}", (section_num, new_subsection_num, 0)
            elif stripped_line.startswith('#### '):
                # 四级标题 -> 子子节
                new_subsubsection_num = subsubsection_num + 1
                return f"#### {target_section}.{section_num}.{subsection_num}.{new_subsubsection_num} {title_text}", (section_num, subsection_num, new_subsubsection_num)
            elif stripped_line.startswith('##### '):
                # 五级标题 -> 子子子节
                new_subsubsection_num = subsubsection_num + 1
                return f"#### {target_section}.{section_num}.{subsection_num}.{new_subsubsection_num} {title_text}", (section_num, subsection_num, new_subsubsection_num)

        # 普通行保持原样
        return line, None

    def _get_title_level(self, line: str) -> int:
        """获取标题级别"""
        stripped = line.strip()
        if stripped.startswith('##### '):
            return 5
        elif stripped.startswith('#### '):
            return 4
        elif stripped.startswith('### '):
            return 3
        elif stripped.startswith('## '):
            return 2
        elif stripped.startswith('# '):
            return 1
        else:
            return 0