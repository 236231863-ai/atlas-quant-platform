"""Strategy Lab 策略实验室页面"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout,
)

from data_loader import load_draws
from stats import hot_numbers, cold_numbers, parity_stats, consecutive_pairs
from engine.evaluation_v2 import get_short_disclaimer

STRATEGIES = [
    {
        "key": "hot",
        "name": "🔥 热号追击",
        "desc": "追踪近期出现频率最高的号码，博取惯性热度延续。",
        "metric": "基于前区出现次数 Top",
    },
    {
        "key": "cold",
        "name": "🧊 冷号潜伏",
        "desc": "关注长期未出的冷号，等待均值回归补出。",
        "metric": "基于前区出现次数 Bottom",
    },
    {
        "key": "balanced",
        "name": "⚖️ 奇偶均衡",
        "desc": "前区奇偶号码按 3:2 均衡配置，降低波动。",
        "metric": "前区奇偶穿插排列",
    },
]


class StrategyPage(QWidget):
    """策略实验室：预置策略卡片，可发起回测。"""

    run_backtest_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel("🧪 策略实验室")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        sub = QLabel("选择策略并进入回测中心验证历史表现。策略基于前区号码统计特征设计。")
        sub.setStyleSheet("color:#8a94a6;font-size:13px;")
        root.addWidget(sub)

        disclaimer = QLabel(get_short_disclaimer())
        disclaimer.setStyleSheet("color:#b08d2a;font-size:12px;font-style:italic;")
        root.addWidget(disclaimer)

        if not self.draws:
            root.addWidget(QLabel("暂无数据"))
            return

        grid = QGridLayout()
        grid.setSpacing(14)
        for i, s in enumerate(STRATEGIES):
            grid.addWidget(self._strategy_card(s), i // 2, i % 2)
        root.addLayout(grid)
        root.addStretch()

    def _strategy_card(self, s):
        card = QFrame()
        card.setStyleSheet(
            "QFrame{background:white;border-radius:12px;border:1px solid #e8ecf2;}"
            "QLabel{background:transparent;}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(8)

        name = QLabel(s["name"])
        name.setStyleSheet("font-size:17px;font-weight:bold;color:#1a1a2e;")
        desc = QLabel(s["desc"])
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#666;font-size:13px;")

        # 实时统计小指标
        stat = QLabel(self._strategy_stat(s["key"]))
        stat.setStyleSheet("color:#2a6df4;font-size:13px;font-weight:bold;")

        btn = QPushButton("▶ 回测此策略")
        btn.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 0;border-radius:6px;font-weight:bold;}"
            "QPushButton:hover{background:#1e56c8;}"
        )
        btn.clicked.connect(lambda checked=False, k=s["key"]: self.run_backtest_requested.emit(k))

        lay.addWidget(name)
        lay.addWidget(desc)
        lay.addWidget(stat)
        lay.addWidget(btn)
        return card

    def _strategy_stat(self, key):
        if not self.draws:
            return ""
        if key == "hot":
            top = hot_numbers(self.draws, 5)
            return "近期热号：" + " ".join(f"{n:02d}" for n, _ in top)
        if key == "cold":
            bot = cold_numbers(self.draws, 5)
            return "近期冷号：" + " ".join(f"{n:02d}" for n, _ in bot)
        p = parity_stats(self.draws)
        return f"当前奇偶比 {p['odd']}:{p['even']}，连号 {consecutive_pairs(self.draws)} 对"
