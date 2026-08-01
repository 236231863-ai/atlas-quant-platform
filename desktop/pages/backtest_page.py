"""Backtest Center 回测中心页面"""
import matplotlib

matplotlib.use("QtAgg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
matplotlib.rcParams["axes.unicode_minus"] = False
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)

from data_loader import load_draws
from stats import recommendation, front_frequency, back_frequency

# 大乐透中奖规则（简化奖金）
PRIZES = [
    ((5, 2), "一等奖", 5_000_000),
    ((5, 1), "二等奖", 180_000),
    ((5, 0), "三等奖", 10_000),
    ((4, 2), "四等奖", 3_000),
    ((4, 1), "五等奖", 300),
    ((3, 2), "六等奖", 200),
    ((4, 0), "七等奖", 100),
    ((3, 1), "八等奖", 15),
    ((2, 2), "八等奖", 15),
    ((3, 0), "九等奖", 5),
    ((1, 2), "九等奖", 5),
    ((2, 1), "九等奖", 5),
    ((0, 2), "九等奖", 5),
]

TICKET_COST = 2


def _grade(front_hit, back_hit):
    for (f, b), name, amount in PRIZES:
        if front_hit >= f and back_hit >= b:
            return name, amount
    return None, 0


class BacktestPage(QWidget):
    """回测中心：选择策略 → 运行回测 → ROI 曲线/回撤/指标。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        header = QLabel("📉 回测中心")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        # 控制栏
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        ctrl.addWidget(QLabel("策略："))
        self.combo = QComboBox()
        self.combo.addItem("热号追击", "hot")
        self.combo.addItem("冷号潜伏", "cold")
        self.combo.addItem("奇偶均衡", "balanced")
        self.combo.setStyleSheet("QComboBox{padding:6px 10px;border:1px solid #d8dee8;border-radius:6px;background:white;}")
        ctrl.addWidget(self.combo)
        self.run_btn = QPushButton("▶ 运行回测")
        self.run_btn.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 20px;border-radius:6px;font-weight:bold;}"
            "QPushButton:hover{background:#1e56c8;}"
        )
        self.run_btn.clicked.connect(self.run_backtest)
        ctrl.addWidget(self.run_btn)
        self.result_label = QLabel("尚未运行回测")
        self.result_label.setStyleSheet("color:#8a94a6;font-size:13px;")
        ctrl.addWidget(self.result_label)
        ctrl.addStretch()
        root.addLayout(ctrl)

        # 图表区
        content = QHBoxLayout()
        content.setSpacing(16)
        self.canvas = FigureCanvas(Figure(figsize=(7, 4), dpi=100))
        content.addWidget(self.canvas, 3)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(
            "background:white;border-radius:10px;border:1px solid #e8ecf2;padding:14px;color:#333;font-size:13px;"
        )
        content.addWidget(self.summary, 2)
        root.addLayout(content, 1)

        # 逐期明细表
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["期号", "推荐前区", "实际前区", "命中", "中奖", "累计收益"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget{font-size:12px;border:1px solid #e8ecf2;border-radius:8px;}"
            "QHeaderView::section{background:#f4f6fa;border:none;padding:6px;font-weight:bold;}"
        )
        root.addWidget(self.table, 1)

    def run_strategy(self, key):
        """从策略页发起回测。"""
        idx = self.combo.findData(key)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)
        self.run_backtest()

    def run_backtest(self):
        if len(self.draws) < 3:
            self.result_label.setText("数据不足")
            return
        method = self.combo.currentData()
        equity = 0.0
        records = []
        hit_counts = []
        # 从第 3 期开始，用前面所有期数做推荐
        for i in range(3, len(self.draws)):
            hist = self.draws[:i]
            rec = recommendation(hist, method)
            actual = self.draws[i]
            front_hit = len(set(rec["front"]) & set(actual.front))
            back_hit = len(set(rec["back"]) & set(actual.back))
            name, amount = _grade(front_hit, back_hit)
            equity += amount - TICKET_COST
            hit_counts.append(front_hit)
            records.append((actual, rec, front_hit, back_hit, name, amount, equity))

        # 指标
        total_bets = len(records)
        win_bets = sum(1 for r in records if r[4])
        total_revenue = sum(r[5] for r in records)
        total_cost = total_bets * TICKET_COST
        roi = (total_revenue - total_cost) / total_cost * 100 if total_cost else 0
        max_dd, dd_start = self._max_drawdown([0.0] + [r[6] for r in records])
        avg_hit = sum(hit_counts) / len(hit_counts)

        self.result_label.setText(f"回测完成：{total_bets} 期，命中率 {win_bets}/{total_bets}")
        self.summary.setText(
            f"**回测结果（{method} 策略）**\n"
            f"· 投注 {total_bets} 期，投入 ¥{total_cost}\n"
            f"· 中奖 {win_bets} 期，奖金 ¥{total_revenue:,.0f}\n"
            f"· 净收益 ¥{total_revenue - total_cost:+,.0f}\n"
            f"· 收益率 {roi:+.1f}%\n"
            f"· 平均前区命中 {avg_hit:.2f} 码\n"
            f"· 最大回撤 ¥{max_dd:,.0f}\n"
        )
        self._draw_curves([0.0] + [r[6] for r in records], records)

        self.table.setRowCount(len(records))
        for row, (d, rec, fh, bh, name, amount, eq) in enumerate(records):
            values = [
                d.number,
                " ".join(f"{n:02d}" for n in rec["front"]),
                d.format_front(),
                f"{fh}+{bh}",
                f"{name} ¥{amount}" if name else "-",
                f"{eq:+,.0f}",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(0x0004 | 0x0080)
                self.table.setItem(row, col, item)

    def _draw_curves(self, equity, records):
        fig = self.canvas.figure
        fig.clear()
        ax1 = fig.add_subplot(111)
        ax1.plot(equity, color="#2a6df4", linewidth=2, label="累计收益")
        ax1.fill_between(range(len(equity)), equity, alpha=0.1, color="#2a6df4")
        ax1.axhline(0, color="gray", linestyle="--")
        ax1.set_title(f"累计收益曲线（{len(records)} 期）")
        ax1.set_xlabel("期序")
        ax1.set_ylabel("收益 (¥)")
        ax1.grid(alpha=0.3)
        fig.tight_layout()
        self.canvas.draw()

    def _max_drawdown(self, equity):
        peak = equity[0]
        max_dd = 0.0
        for v in equity:
            if v > peak:
                peak = v
            dd = peak - v
            if dd > max_dd:
                max_dd = dd
        return max_dd, 0
