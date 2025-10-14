"""
文档数据模型
定义文档结构和相关操作
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from config.settings import SECTION_KEYWORDS, SECTION_THRESHOLDS


@dataclass
class Title:
    """标题信息"""
    level: int
    number: str
    text: str
    line_index: int


@dataclass
class Section:
    """部分信息"""
    number: str
    title: str
    titles: List[Title]


class Document:
    """文档类"""

    def __init__(self):
        self.lines: List[str] = []
        self.sections: Dict[str, Section] = {}
        self.titles: List[Title] = []

        # 标题模式
        self.title_pattern = re.compile(r'^(#+)\s+(\d+(\.\d+)*\s+)?(.*)$')

    def load_from_lines(self, lines: List[str]) -> None:
        """从行列表加载文档"""
        self.lines = lines.copy()
        self._parse_document()

    def load_from_content(self, content: str) -> None:
        """从内容字符串加载文档"""
        self.lines = content.splitlines(keepends=True)
        self._parse_document()

    def _parse_document(self) -> None:
        """解析文档结构"""
        self.sections.clear()
        self.titles.clear()

        current_section = None

        for i, line in enumerate(self.lines):
            title = self._parse_title(line, i)
            if title:
                self.titles.append(title)

                # 更新部分信息
                if title.level == 2 and title.number:
                    section_num = title.number.split('.')[0]
                    current_section = section_num
                    if current_section not in self.sections:
                        self.sections[current_section] = Section(
                            number=current_section,
                            title=title.text,
                            titles=[]
                        )

                if current_section and current_section in self.sections:
                    self.sections[current_section].titles.append(title)

    def _parse_title(self, line: str, line_index: int) -> Optional[Title]:
        """解析标题行"""
        match = self.title_pattern.match(line.strip())
        if not match:
            return None

        level = len(match.group(1))
        number = match.group(2).strip() if match.group(2) else None
        text = match.group(4).strip()

        # 忽略无编号的一级标题
        if level == 1 and not number:
            return None

        return Title(level=level, number=number, text=text, line_index=line_index)

    def determine_target_section(self, content: str) -> Tuple[str, bool]:
        """确定目标部分
        返回: (section_number, is_new_section)
        """
        content_lower = content.lower()
        section_scores = {sec: 0 for sec in SECTION_KEYWORDS.keys()}

        # 计算各部分的关键词匹配得分
        for section, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in content_lower:
                    section_scores[section] += 1

        # 找到得分最高的部分和得分
        max_score = max(section_scores.values())

        # 如果没有匹配到任何关键词，创建新部分
        if max_score == 0:
            # 找到最大的现有部分编号
            existing_sections = [int(s) for s in self.sections.keys() if s.isdigit()]
            next_section = str(max(existing_sections) + 1) if existing_sections else "7"
            return next_section, True

        # 获取得分最高的部分
        best_section = max(section_scores, key=lambda k: section_scores[k])

        # 判断是否为全新部分：得分低于阈值或内容结构表明是独立部分
        is_new_section = (
            section_scores[best_section] < SECTION_THRESHOLDS.get(best_section, 3) or
            self._is_independent_section(content)
        )

        # 如果判断为全新部分，使用下一个可用的部分编号
        if is_new_section:
            existing_sections = [int(s) for s in self.sections.keys() if s.isdigit()]
            next_section = str(max(existing_sections) + 1) if existing_sections else "7"
            return next_section, True

        return best_section, False

    def _is_independent_section(self, content: str) -> bool:
        """判断内容是否为独立部分（而非融入现有部分）"""
        lines = content.split('\n')

        # 检查是否有高级别的标题（表明是独立部分）
        has_high_level_title = any(
            line.strip().startswith(('# ', '## ', '### ')) and
            any(keyword in line.lower() for keyword in ['基础', '核心', '相关', '技术'])
            for line in lines[:10]  # 只检查前10行
        )

        # 检查内容长度（长内容更可能是独立部分）
        is_long_content = len(content.strip()) > 1000

        # 检查是否有多个子章节
        subsection_titles = [line for line in lines if line.strip().startswith('### ')]
        has_multiple_subsections = len(subsection_titles) > 2

        # 检查是否有中文数字标题（表明是独立的结构化内容）
        has_chinese_titles = any(
            re.match(r'^[一二三四五六七八九十]、', line.strip()) for line in lines
        )

        return has_high_level_title or is_long_content or has_multiple_subsections or has_chinese_titles

    def insert_content(self, content: str, section: str) -> None:
        """插入内容到指定部分"""
        # 查找插入位置
        insert_pos = self._find_insert_position(section)

        # 插入内容
        content_lines = content.splitlines(keepends=True)
        if not content_lines[-1].endswith('\n'):
            content_lines[-1] += '\n'

        # 在插入位置添加内容
        self.lines[insert_pos:insert_pos] = ['\n'] + content_lines + ['\n']

        # 重新解析文档
        self._parse_document()

    def _find_insert_position(self, section: str) -> int:
        """查找插入位置"""
        # 如果section不存在于当前文档中，插入到文档末尾
        if section not in self.sections:
            return len(self.lines)

        # 如果section存在，找到该部分的最后一个标题位置
        section_titles = self.sections[section].titles
        if not section_titles:
            return len(self.lines)

        # 找到该部分最后一个标题的行号
        last_title_line = max(title.line_index for title in section_titles)

        # 从最后一个标题开始向后查找，直到遇到下一个部分标题或文件结尾
        for i in range(last_title_line + 1, len(self.lines)):
            line = self.lines[i].strip()
            if line.startswith('## ') and not line.startswith(f'## {section}.'):
                # 找到了下一个部分，在这里插入
                return i
            elif i == len(self.lines) - 1:
                # 文件结尾
                return i + 1

        return len(self.lines)

    def get_content_lines(self) -> List[str]:
        """获取文档内容行"""
        return self.lines

    def get_content(self) -> str:
        """获取文档内容字符串"""
        return ''.join(self.lines)