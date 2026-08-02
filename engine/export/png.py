"""export - PNG 图表导出。"""
from __future__ import annotations

import os


class PNGExporter:
    """将 matplotlib Figure 导出为 PNG。"""

    @staticmethod
    def export_figure(fig, path: str, dpi: int = 150) -> str:
        """保存 matplotlib Figure 到 PNG，返回路径。"""
        if not path.lower().endswith(".png"):
            path += ".png"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        return path

    @staticmethod
    def export_canvas(canvas, path: str, dpi: int = 150) -> str:
        """保存 Qt FigureCanvas 到 PNG（桌面图表）。"""
        return PNGExporter.export_figure(canvas.figure, path, dpi)
