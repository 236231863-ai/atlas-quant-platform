"""export - Markdown 导出。"""
from __future__ import annotations

import os
from typing import List


class MarkdownExporter:
    """将结构化内容导出为 Markdown 文件。"""

    @staticmethod
    def export(content: str, path: str) -> str:
        """写入 .md 文件，返回最终路径。"""
        if not path.lower().endswith(".md"):
            path += ".md"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def from_sections(title: str, sections: List[tuple], path: str) -> str:
        """由 (小标题, 正文列表) 组装成 Markdown。

        Args:
            title: 文档标题
            sections: [(heading, [line, ...]), ...]
            path: 输出路径
        """
        parts = [f"# {title}", ""]
        for heading, lines in sections:
            parts.append(f"## {heading}")
            parts.append("")
            for line in lines:
                parts.append(f"- {line}" if not line.startswith((" ", "-", "|", "**")) else line)
            parts.append("")
        return MarkdownExporter.export("\n".join(parts), path)
