"""
配置常量
"""

# 各部分的关键词映射
SECTION_KEYWORDS = {
    '1': ['rocky linux', 'rsync', 'cron', 'ssh', '系统工具', '权限', '进程', 'jpress'],
    '2': ['nfs', '网络文件系统', 'exports', 'mount', 'umount'],
    '3': ['python', 'venv', 'miniconda', 'pip', 'gunicorn', 'supervisord', 'pyenv'],
    '4': ['http', 'dns', '网络', 'cdn', 'inode', 'acme', 'session', 'cookie', 'tcp', 'pv', 'uv'],
    '5': ['nginx', '软链接', '硬链接', '进程模型', '负载均衡', '动静分离'],
    '6': ['keepalived', '高可用', '脑裂', '集群', 'vrrp', '健康检查'],
    '7': ['terraform', 'hcl', 'provider', '状态文件', '基础设施即代码']
}

# 各部分的关键词匹配阈值（低于此阈值则视为全新部分）
SECTION_THRESHOLDS = {
    '1': 2,
    '2': 2,
    '3': 2,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 1  # Terraform相关内容较少，降低阈值
}

# 支持的文本文件扩展名
TEXT_FILE_EXTENSIONS = ['.txt', '.md', '.markdown', '.text']