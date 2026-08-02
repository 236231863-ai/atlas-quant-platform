"""export - PDF 导出（fpdf2）。

将报告文本 / 回测明细导出为 PDF。
中文需嵌入字体：优先系统 SimHei/微软雅黑，缺失时用英文提示。
"""
from __future__ import annotations

import os
from typing import List, Optional


class PDFExporter:
    """基于 fpdf2 的 PDF 导出器。"""

    _font_candidates = [
        r"C:\Windows\Fonts\msyh.ttc",   # 微软雅黑
        r"C:\Windows\Fonts\simhei.ttf",  # 黑体
        r"C:\Windows\Fonts\simsun.ttc",  # 宋体
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    _bold_font_candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc",  # 微软雅黑粗体
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]

    @classmethod
    def _resolve_font(cls) -> Optional[str]:
        for p in cls._font_candidates:
            if os.path.exists(p):
                return p
        return None

    @classmethod
    def _resolve_bold_font(cls) -> Optional[str]:
        for p in cls._bold_font_candidates:
            if os.path.exists(p):
                return p
        return None

    @staticmethod
    def _register_font(pdf) -> Optional[str]:
        """注册中文字体（常规 + 粗体用独立字体文件），返回常规字体路径；失败返回 None。"""
        font = PDFExporter._resolve_font()
        if font:
            try:
                pdf.add_font("cn", "", font)
                bold = PDFExporter._resolve_bold_font() or font
                pdf.add_font("cn", "B", bold)
                return font
            except Exception:
                return None
        return None

    @staticmethod
    def export_report(title: str, lines: List[str], path: str) -> str:
        """将文本行导出为 PDF（按页自动换行）。

        Args:
            title: 文档标题
            lines: 文本行（支持 "**加粗**" 前缀标记）
            path: 输出路径（.pdf）
        """
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()

        font = PDFExporter._register_font(pdf)

        def _write(text: str, size: int, bold: bool):
            if font:
                pdf.set_font("cn", "B" if bold else "", size)
            else:
                pdf.set_font("Helvetica", "B" if bold else "", size)
            pdf.write(size * 0.5 + 2, text)
            pdf.ln(size * 0.5 + 2)

        _write(title, 16, True)
        pdf.ln(3)
        for line in lines:
            if not line:
                pdf.ln(2)
                continue
            bold = line.startswith("**") and line.endswith("**")
            clean = line.strip("*").strip() if bold else line
            _write(clean, 11, bold)
        pdf.output(path)
        return path

    @staticmethod
    def export_backtest(records: list, summary_lines: List[str], path: str) -> str:
        """导出回测报告 PDF：摘要 + 逐期明细表。"""
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()
        font = PDFExporter._register_font(pdf)

        def _set(size: int, bold: bool):
            if font:
                pdf.set_font("cn", "B" if bold else "", size)
            else:
                pdf.set_font("Helvetica", "B" if bold else "", size)

        _set(15, True)
        pdf.write(8, "Atlas 回测报告")
        pdf.ln(10)
        _set(10, False)
        for line in summary_lines:
            pdf.write(6, line.strip("*").strip())
            pdf.ln(7)
        pdf.ln(4)

        # 明细表
        headers = ["期号", "推荐前区", "实际前区", "命中", "中奖", "累计"]
        col_w = [18, 38, 38, 20, 34, 22]
        _set(9, True)
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 7, h, border=1)
        pdf.ln()
        _set(8, False)
        for r in records[:200]:  # 限制行数防撑爆
            vals = [
                str(r.issue),
                r.recommended[:12],
                r.actual[:12],
                f"{r.front_hit}+{r.back_hit}",
                f"{r.prize_name or '-'}",
                f"{r.equity:+,.0f}",
            ]
            for i, v in enumerate(vals):
                pdf.cell(col_w[i], 6, v[:col_w[i] // 3 + 2], border=1)
            pdf.ln()
        pdf.output(path)
        return path
