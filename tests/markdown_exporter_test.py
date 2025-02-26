import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.utils.markdown_exporter import save_as_markdown

content = """
# 这是一个标题

这是一些Markdown内容，
包括列表：
- 项目1
- 项目2
"""
save_as_markdown(content, 'assets/output.md')

