"""
内容清理工具
负责清理和标准化Markdown内容
"""

import re


def clean_markdown_content(content: str) -> str:
    """清理Markdown内容，统一格式"""
    lines = [line.rstrip('\n') for line in content.split('\n')]
    cleaned_groups = []
    current_group = []

    # 第一步：按空行分割内容
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            if current_group:
                cleaned_groups.append(current_group)
                current_group = []
            continue
        current_group.append(line)

    if current_group:
        cleaned_groups.append(current_group)

    # 第二步：处理每个组
    processed_groups = []
    for group in cleaned_groups:
        # 判断是否为表格组
        is_table_group = any(
            (clean_line := line.strip())
            and clean_line.startswith('|')
            and clean_line.count('|') >= 2
            for line in group
        )

        if is_table_group:
            processed_groups.append('\n'.join(group))
        else:
            # 对于非表格组，确保标题行格式正确
            processed_group = []
            for line in group:
                # 清理标题行中的多余空格
                stripped = line.strip()
                if stripped.startswith('#'):
                    # 确保#号和标题内容之间有空格
                    cleaned_line = re.sub(r'^(#+)\s*', r'\1 ', stripped)
                    processed_group.append(cleaned_line)
                else:
                    processed_group.append(line)

            processed_groups.append('\n\n'.join(processed_group))

    return '\n\n'.join(processed_groups)