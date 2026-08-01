"""Data Analysis 统计图表页面"""
import matplotlib

matplotlib.use("QtAgg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
)

from data_loader import load_draws
from stats import (
    front_frequency, back_frequency, front_sums, front_spans,
    parity_stats, consecutive_pairs,
)

_CHARTS = ["frequency", "sum", "span", "parity"]


class AnalysisPage(QWidget):
    """数据分析：前区频率、和值、跨度、奇偶分布。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._current = "frequency"
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel("📈 数据分析")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        if not self.draws:
            root.addWidget(QLabel("暂无数据"))
            return

        # 图表类型按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._btns = {}
        specs = [
            ("frequency", "频率分布"),
            ("sum", "和值分布"),
            ("span", "跨度分布"),
            ("parity", "奇偶分布"),
        ]
        for key, text in specs:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setStyleSheet(self._btn_style(False))
            b.clicked.connect(lambda checked=False, k=key: self._switch(k))
            btn_row.addWidget(b)
            self._btns[key] = b
        btn_row.addStretch()
        root.addLayout(btn_row)

        # 图表区 + 摘要
        content = QHBoxLayout()
        content.setSpacing(16)
        self.canvas = FigureCanvas(Figure(figsize=(7, 4), dpi=100))
        content.addWidget(self.canvas, 3)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(
            "background:white;border-radius:10px;border:1px solid #e8ecf2;"
            "padding:14px;color:#444;font-size:13px;line-height:1.6;"
        )
        content.addWidget(self.summary, 2)
        root.addLayout(content, 1)

        self._switch("frequency")

    def _btn_style(self, active):
        if active:
            return "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 16px;border-radius:6px;font-weight:bold;}"
        return "QPushButton{background:white;color:#444;border:1px solid #d8dee8;padding:8px 16px;border-radius:6px;}"

    def _switch(self, key):
        self._current = key
        for k, b in self._btns.items():
            b.setChecked(k == key)
            b.setStyleSheet(self._btn_style(k == key))
        self._render()

    def _render(self):
        fig = self.canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        text = ""
        if self._current == "frequency":
            freq = front_frequency(self.draws)
            nums = list(freq.keys())
            vals = list(freq.values())
            ax.bar(nums, vals, color="#2a6df4", width=0.7)
            ax.set_title("前区号码频率分布")
            ax.set_xlabel("号码")
            ax.set_ylabel("出现次数")
            ax.set_xticks(range(1, 36, 2))
            top = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
            text = (f"**前区频率 TOP5**\n" + "\n".join(f"号码 {n:02d}：{c} 次" for n, c in top[:5])
                    + f"\n\n平均每码 {sum(vals) / len(vals):.1f} 次")
        elif self._current == "sum":
            sums = front_sums(self.draws)
            ax.hist(sums, bins=8, color="#f59e0b", edgecolor="white")
            ax.set_title("前区和值分布")
            ax.set_xlabel("和值")
            ax.set_ylabel("期数")
            avg = sum(sums) / len(sums)
            text = f"**和值区间**：{min(sums)} - {max(sums)}\n\n平均和值：{avg:.0f}\n\n和值反映号码整体大小，大乐透前区和值常见区间 60-120。"
        elif self._current == "span":
            spans = front_spans(self.draws)
            ax.hist(spans, bins=6, color="#10b981", edgecolor="white")
            ax.set_title("前区跨度分布")
            ax.set_xlabel("跨度（最大-最小）")
            ax.set_ylabel("期数")
            avg = sum(spans) / len(spans)
            text = f"**跨度区间**：{min(spans)} - {max(spans)}\n\n平均跨度：{avg:.0f}\n\n跨度反映号码离散程度，跨度大说明号码分布广。"
        elif self._current == "parity":
            p = parity_stats(self.draws)
            ax.pie(
                [p["odd"], p["even"]],
                labels=["奇数", "偶数"],
                colors=["#ef4444", "#3b82f6"],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.set_title("前区奇偶分布")
            odd_pct = p["odd"] / (p["odd"] + p["even"]) * 100
            text = (f"奇数 {p['odd']} 次 ({odd_pct:.0f}%)，偶数 {p['even']} 次 ({100 - odd_pct:.0f}%)"
                    f"\n\n连号对数：{consecutive_pairs(self.draws)}")
        fig.tight_layout()
        self.canvas.draw()
        self.summary.setText(self._to_plain(text))

    def _to_plain(self, md):
        import re

        return re.sub(r"\*\*(.+?)\*\*", r"\1", md)
