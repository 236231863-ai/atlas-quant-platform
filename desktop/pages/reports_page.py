"""Reports 研究报告页面"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QFileDialog,
)

from data_loader import load_draws
from stats import (
    front_frequency, back_frequency, hot_numbers, cold_numbers, parity_stats,
    front_sums, front_spans, consecutive_pairs,
)
from engine.export import MarkdownExporter, PDFExporter, CSVExporter


class ReportsPage(QWidget):
    """研究报告：一键生成统计分析报告。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QLabel("📄 研究报告")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        row = QHBoxLayout()
        gen = QPushButton("🔄 生成统计报告")
        gen.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 20px;border-radius:8px;font-weight:bold;}"
            "QPushButton:hover{background:#1e56c8;}"
        )
        gen.clicked.connect(self._generate)
        row.addWidget(gen)

        btn_md = QPushButton("⬇ 导出 Markdown")
        btn_pdf = QPushButton("⬇ 导出 PDF")
        btn_csv = QPushButton("⬇ 导出 CSV")
        for b in (btn_md, btn_pdf, btn_csv):
            b.setStyleSheet(
                "QPushButton{background:#eef4ff;color:#1e56c8;border:none;padding:8px 14px;border-radius:8px;font-weight:bold;}"
                "QPushButton:hover{background:#dbe9ff;}"
            )
        btn_md.clicked.connect(lambda: self._export("md"))
        btn_pdf.clicked.connect(lambda: self._export("pdf"))
        btn_csv.clicked.connect(lambda: self._export("csv"))
        row.addWidget(btn_md)
        row.addWidget(btn_pdf)
        row.addWidget(btn_csv)
        row.addWidget(QLabel("所有分析结果可保存"))
        row.addStretch()
        root.addLayout(row)

        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #e8ecf2;border-radius:10px;font-size:13px;padding:14px;line-height:1.7;}"
        )
        root.addWidget(self.view, 1)
        self._generate()

    def _generate(self):
        if not self.draws:
            self.view.setPlainText("暂无数据")
            return
        last = self.draws[-1]
        sums = front_sums(self.draws)
        spans = front_spans(self.draws)
        p = parity_stats(self.draws)
        hot = hot_numbers(self.draws, 10)
        cold = cold_numbers(self.draws, 10)
        fq = front_frequency(self.draws)
        bq = back_frequency(self.draws)
        top_back = sorted(bq.items(), key=lambda kv: kv[1], reverse=True)[:5]

        lines = []
        lines.append("=" * 42)
        lines.append("  大乐透（DLT）数据分析报告")
        lines.append(f"  数据范围：{self.draws[0].draw_date} ~ {last.draw_date}  共 {len(self.draws)} 期")
        lines.append("=" * 42)
        lines.append("")
        lines.append("【一、总体概览】")
        lines.append(f"  · 样本期数：{len(self.draws)} 期")
        lines.append(f"  · 最新期号：{last.number}（{last.draw_date}）")
        lines.append(f"  · 最新前区：{last.format_front()}  +  {last.format_back()}")
        lines.append(f"  · 最新奖池：{last.format_pool()}")
        lines.append(f"  · 平均和值：{sum(sums) / len(sums):.0f}（区间 {min(sums)}-{max(sums)}）")
        lines.append(f"  · 平均跨度：{sum(spans) / len(spans):.0f}（区间 {min(spans)}-{max(spans)}）")
        lines.append(f"  · 奇偶比：{p['odd']}:{p['even']}，连号 {consecutive_pairs(self.draws)} 对")
        lines.append("")
        lines.append("【二、前区号码频率 TOP10】")
        for n, c in hot:
            bar = "█" * c
            lines.append(f"  {n:02d}  {c}次  {bar}")
        lines.append("")
        lines.append("【三、前区冷号 BOTTOM10】")
        for n, c in cold:
            lines.append(f"  {n:02d}  {c}次")
        lines.append("")
        lines.append("【四、后区号码频率 TOP5】")
        for n, c in top_back:
            lines.append(f"  {n:02d}  {c}次")
        lines.append("")
        lines.append("【五、策略推荐（仅供参考）】")
        from stats import recommendation

        for method, label in [("hot", "热号策略"), ("cold", "冷号策略"), ("balanced", "奇偶均衡")]:
            rec = recommendation(self.draws, method)
            lines.append(f"  · {label}：{' '.join(f'{n:02d}' for n in rec['front'])}  +  "
                         f"{' '.join(f'{n:02d}' for n in rec['back'])}")
        lines.append("")
        lines.append("【免责声明】本报告基于历史数据统计，彩票开奖为随机事件，结果仅供研究参考。")
        self.lines = lines
        self.view.setPlainText("\n".join(lines))

    def show_report(self, report: dict) -> None:
        """展示外部传入的报告（FirstSuccessFlow 自动生成的第一份报告）。"""
        lines = report.get("lines") or []
        title = report.get("title", "分析报告")
        text = [f"📄 {title}", "=" * 42]
        if report.get("latest_issue"):
            text.append(f"最新期号：{report['latest_issue']}（{report.get('latest_date','')}）")
        if report.get("latest_numbers"):
            text.append(f"最新号码：{report['latest_numbers']}")
        text += lines
        if report.get("disclaimer"):
            text.append("")
            text.append(f"【免责声明】{report['disclaimer']}")
        self.lines = text
        self.view.setPlainText("\n".join(text))

    def _export(self, fmt: str) -> None:
        """导出当前报告为 MD / PDF / CSV。"""
        if not getattr(self, "lines", None):
            return
        default_name = f"Atlas_报告_{self.draws[-1].number if self.draws else 'v3.6.1'}"
        # 行为追踪
        try:
            from engine.user_feedback_v2 import UserFeedbackTracker
            UserFeedbackTracker().report_export(fmt, kind="report")
        except Exception:
            pass
        try:
            from engine.user_intelligence.v3 import UserIntelligenceV3
            UserIntelligenceV3().report_export(fmt)
        except Exception:
            pass
        if fmt == "md":
            path, _ = QFileDialog.getSaveFileName(self, "导出 Markdown", default_name + ".md", "Markdown (*.md)")
            if path:
                MarkdownExporter.export(self.view.toPlainText(), path)
        elif fmt == "pdf":
            path, _ = QFileDialog.getSaveFileName(self, "导出 PDF", default_name + ".pdf", "PDF (*.pdf)")
            if path:
                PDFExporter.export_report(
                    "Atlas 数据分析报告",
                    self.lines,
                    path,
                )
        elif fmt == "csv":
            path, _ = QFileDialog.getSaveFileName(self, "导出 CSV", default_name + ".csv", "CSV (*.csv)")
            if path:
                # 将报告文本存为单列 CSV（便于通用工具打开）
                CSVExporter.export(
                    ["line"],
                    [[l] for l in self.lines],
                    path,
                )
