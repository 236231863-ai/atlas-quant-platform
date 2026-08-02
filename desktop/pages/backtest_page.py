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
    QFileDialog,
)

from data_loader import load_draws
from stats import recommendation, front_frequency, back_frequency
from engine.evaluation_v2 import run_backtest_with_evaluation, get_short_disclaimer
from engine.export import CSVExporter, PDFExporter, PNGExporter

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

        btn_csv = QPushButton("⬇ 明细 CSV")
        btn_pdf = QPushButton("⬇ 报告 PDF")
        btn_png = QPushButton("⬇ 图表 PNG")
        for b in (btn_csv, btn_pdf, btn_png):
            b.setStyleSheet(
                "QPushButton{background:#eef4ff;color:#1e56c8;border:none;padding:7px 12px;border-radius:7px;font-weight:bold;font-size:12px;}"
                "QPushButton:hover{background:#dbe9ff;}"
            )
        btn_csv.clicked.connect(lambda: self._export("csv"))
        btn_pdf.clicked.connect(lambda: self._export("pdf"))
        btn_png.clicked.connect(lambda: self._export("png"))
        ctrl.addWidget(btn_csv)
        ctrl.addWidget(btn_pdf)
        ctrl.addWidget(btn_png)

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
        try:
            report = run_backtest_with_evaluation(self.draws, method=method)
        except Exception as e:  # 兜底：评估失败不崩溃
            self.result_label.setText(f"回测异常：{e}")
            return

        n = report.n_bets_total
        win_bets = sum(1 for r in report.records if r.prize_name)
        self.result_label.setText(f"回测完成：{n} 期，命中率 {win_bets}/{n}")

        self.summary.setText(
            f"**回测结果（{method} 策略）**\n"
            f"· 投注 {n} 期（样本内 {report.n_bets_train} / 样本外 {report.n_bets_oos}）\n"
            f"· 总收益率 {report.roi_total:+.1f}%\n"
            f"· 样本内 ROI {report.roi_train:+.1f}% / 样本外 ROI {report.roi_oos:+.1f}%\n"
            f"· 随机基准 ROI 均值 {report.baseline_roi_mean:+.1f}%\n"
            f"  （90% 区间 {report.baseline_roi_p5:+.1f}% ~ {report.baseline_roi_p95:+.1f}%）\n"
            f"· 超额收益 {report.excess_roi:+.1f}%\n"
            f"· 平均前区命中 {report.avg_front_hit:.2f} 码 / 最大回撤 ¥{report.max_drawdown:,.0f}\n"
            f"· 结论：{'高于随机基准区间，但需谨慎' if report.better_than_random else '未显著优于随机选号'}\n\n"
            f"{get_short_disclaimer()}"
        )
        equities = [0.0] + [r.equity for r in report.records]
        self._draw_curves(equities, report.records)

        self.table.setRowCount(len(report.records))
        for row, r in enumerate(report.records):
            values = [
                r.issue,
                r.recommended,
                r.actual,
                f"{r.front_hit}+{r.back_hit}",
                f"{r.prize_name} ¥{r.amount:,.0f}" if r.prize_name else "-",
                f"{r.equity:+,.0f}",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(0x0004 | 0x0080)
                self.table.setItem(row, col, item)
        self._report = report

    def _export(self, fmt: str) -> None:
        """导出回测结果：CSV 明细 / PDF 报告 / PNG 图表。"""
        report = getattr(self, "_report", None)
        if report is None or not report.records:
            self.result_label.setText("请先运行回测")
            return
        base = f"Atlas_回测_{report.method}"
        if fmt == "csv":
            path, _ = QFileDialog.getSaveFileName(self, "导出明细 CSV", base + ".csv", "CSV (*.csv)")
            if path:
                CSVExporter.export_records(report.records, path)
                self.result_label.setText("明细已导出 CSV")
        elif fmt == "pdf":
            path, _ = QFileDialog.getSaveFileName(self, "导出报告 PDF", base + ".pdf", "PDF (*.pdf)")
            if path:
                summary = [
                    f"策略: {report.method}",
                    f"投注 {report.n_bets_total} 期（样本内 {report.n_bets_train}/样本外 {report.n_bets_oos}）",
                    f"总 ROI {report.roi_total:+.1f}% | 样本外 ROI {report.roi_oos:+.1f}%",
                    f"随机基准 ROI 均值 {report.baseline_roi_mean:+.1f}%",
                    f"结论: {'高于随机基准，需谨慎' if report.better_than_random else '未显著优于随机选号'}",
                    get_short_disclaimer(),
                ]
                PDFExporter.export_backtest(report.records, summary, path)
                self.result_label.setText("报告已导出 PDF")
        elif fmt == "png":
            path, _ = QFileDialog.getSaveFileName(self, "保存图表 PNG", base + ".png", "PNG (*.png)")
            if path:
                PNGExporter.export_canvas(self.canvas, path)
                self.result_label.setText("图表已保存 PNG")

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
