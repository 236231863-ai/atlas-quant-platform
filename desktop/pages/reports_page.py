"""Reports 研究报告页面"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
)

from data_loader import load_draws
from stats import (
    front_frequency, back_frequency, hot_numbers, cold_numbers, parity_stats,
    front_sums, front_spans, consecutive_pairs,
)


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
        row.addWidget(QLabel("基于本地开奖数据自动生成，可复制保存"))
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
        self.view.setPlainText("\n".join(lines))
