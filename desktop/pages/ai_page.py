"""AI Assistant 智能分析助手页面（本地统计驱动）"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
)

from data_loader import load_draws
from stats import (
    front_frequency, back_frequency, hot_numbers, cold_numbers, parity_stats,
    front_sums, front_spans, consecutive_pairs, recommendation,
)


class AIPage(QWidget):
    """AI 助手：基于本地开奖统计的智能问答。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QLabel("🤖 AI 智能助手")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #e8ecf2;border-radius:10px;font-size:13px;padding:12px;}"
        )
        root.addWidget(self.chat, 1)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.input = QTextEdit()
        self.input.setFixedHeight(60)
        self.input.setPlaceholderText("输入问题，如：给我推荐下期号码 / 哪些是热号？")
        self.input.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #d8dee8;border-radius:8px;font-size:13px;padding:8px;}"
        )
        row.addWidget(self.input, 1)
        send = QPushButton("发送")
        send.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:10px 22px;border-radius:8px;font-weight:bold;}"
            "QPushButton:hover{background:#1e56c8;}"
        )
        send.clicked.connect(self._send)
        row.addWidget(send)
        root.addLayout(row)

        self._append("assistant", "你好，我是 Atlas 数据分析助手。你可以问我：\n"
                                  "· 推荐下期号码（热号/冷号/均衡）\n"
                                  "· 热号有哪些？冷号有哪些？\n"
                                  "· 当前奇偶分布 / 和值 / 跨度情况\n"
                                  "· 奖池数据概览")

    def _append(self, role, text):
        prefix = "🧑 你" if role == "user" else "🤖 Atlas"
        color = "#2a6df4" if role == "user" else "#1a1a2e"
        self.chat.append(f'<div style="color:{color};font-weight:bold;">{prefix}</div>')
        self.chat.append(f'<div style="color:#444;margin-bottom:8px;">{text}</div>')

    def _send(self):
        q = self.input.toPlainText().strip()
        if not q:
            return
        self._append("user", q)
        self.input.clear()
        self._append("assistant", self._answer(q))

    def _answer(self, q):
        if not self.draws:
            return "暂无数据，无法分析。"
        ql = q.lower()
        last = self.draws[-1]
        if "热号" in ql:
            hot = hot_numbers(self.draws, 8)
            return "近期热号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in hot)
        if "冷号" in ql:
            cold = cold_numbers(self.draws, 8)
            return "近期冷号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in cold)
        if "推荐" in ql or "号码" in ql or "一注" in ql:
            method = "hot"
            if "冷" in ql:
                method = "cold"
            elif "均衡" in ql:
                method = "balanced"
            rec = recommendation(self.draws, method)
            base = "均衡策略" if method == "balanced" else ("冷号策略" if method == "cold" else "热号策略")
            return (f"按【{base}】推荐一注大乐透：\n"
                    f"前区：{' '.join(f'{n:02d}' for n in rec['front'])}\n"
                    f"后区：{' '.join(f'{n:02d}' for n in rec['back'])}\n"
                    f"（仅基于历史统计，供研究参考）")
        if "奇偶" in ql:
            p = parity_stats(self.draws)
            return f"前区奇偶：奇数 {p['odd']} 次，偶数 {p['even']} 次，比值约 {p['odd'] / (p['odd'] + p['even']) * 100:.0f}:{p['even'] / (p['odd'] + p['even']) * 100:.0f}"
        if "和值" in ql:
            sums = front_sums(self.draws)
            return (f"前区和值区间 {min(sums)}-{max(sums)}，平均 {sum(sums) / len(sums):.0f}，"
                    f"最新一期和值 {last.front_sum}")
        if "跨度" in ql:
            spans = front_spans(self.draws)
            return f"前区跨度区间 {min(spans)}-{max(spans)}，平均 {sum(spans) / len(spans):.0f}"
        if "奖池" in ql or "概览" in ql or "总览" in ql:
            return (f"当前样本 {len(self.draws)} 期，最新期 {last.number}（{last.draw_date}），"
                    f"最新奖池 {last.format_pool()}，连号 {consecutive_pairs(self.draws)} 对。")
        return ("我可以分析本地开奖数据。请尝试问：\n"
                "· “推荐下期号码”\n· “热号有哪些”\n· “奇偶分布如何”\n· “和值/跨度/奖池”")
