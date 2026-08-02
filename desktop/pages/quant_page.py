"""彩票量化中心页面（v3.9.0 Phase 8）。

工作台「🎯 彩票量化分析」入口 → 量化中心：
  1. 组合评分   StructureAnalyzer
  2. 概率分析   ProbabilityModel
  3. 模拟报告   SimulationEngine（蒙特卡洛）
  4. 资金风险   RiskEngine
  5. 策略回测   StrategyBacktester

所有输出含随机性声明，禁止"预测中奖/提高中奖概率"表达。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QMessageBox,
)

from data_loader import load_draws


class QuantPage(QWidget):
    """彩票量化中心。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        header = QLabel("🎯 彩票量化中心")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        sub = QLabel("统计分析 · 概率计算 · 蒙特卡洛模拟 · 资金风险 · 策略回测")
        sub.setStyleSheet("color:#666;font-size:12px;")
        root.addWidget(sub)

        # 号码输入
        root.addWidget(QLabel("投注号码（每注 5 前区 + 2 后区，可多注）："))
        self.input = QTextEdit()
        self.input.setFixedHeight(90)
        self.input.setPlaceholderText("例如：10111822350612 01020304050607（连续号码串）\n或点击「从票据读取」")
        self.input.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #d8dee8;border-radius:8px;font-size:13px;padding:8px;}"
        )
        root.addWidget(self.input)

        # 操作行
        row = QHBoxLayout()
        row.setSpacing(8)
        btns = [
            ("🏷 组合评分", self._run_structure),
            ("🎲 概率分析", self._run_probability),
            ("🎰 模拟报告", self._run_simulation),
            ("💰 资金风险", self._run_risk),
            ("📈 策略回测", self._run_backtest),
        ]
        for text, handler in btns:
            b = QPushButton(text)
            b.setStyleSheet(
                "QPushButton{background:#2a6df4;color:white;border:none;"
                "padding:8px 10px;border-radius:6px;font-size:12px;}"
                "QPushButton:hover{background:#1e56c8;}"
            )
            b.clicked.connect(handler)
            row.addWidget(b)
        from_tickets = QPushButton("📂 从票据读取")
        from_tickets.setStyleSheet(
            "QPushButton{background:white;color:#2a6df4;border:1px solid #2a6df4;"
            "padding:8px 10px;border-radius:6px;font-size:12px;}"
        )
        from_tickets.clicked.connect(self._load_from_tickets)
        row.addWidget(from_tickets)
        row.addStretch()
        root.addLayout(row)

        # 结果
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #e8ecf2;border-radius:8px;"
            "font-size:13px;padding:10px;font-family:'Microsoft YaHei',monospace;}"
        )
        root.addWidget(self.result, 1)

        self._append_result(
            "欢迎使用彩票量化分析。请粘贴号码或从票据读取，然后选择分析功能。\n\n"
            "⚠️ 本中心仅提供统计分析、概率计算、历史研究与风险管理。"
            "彩票开奖结果具有随机性，任何号码组合中奖概率相同。"
        )

    def _append_result(self, text):
        self.result.append(text)

    def _get_tickets(self):
        """从输入解析号码。"""
        text = self.input.toPlainText().strip()
        from engine.lottery_intent.ticket_parser import TicketParser
        parse = TicketParser.parse(text)
        return parse.to_ticket_dicts(), parse.lottery or "dlt"

    def _load_from_tickets(self):
        """从票据系统读取。"""
        try:
            from engine.ticket_system import TicketManager
            mgr = TicketManager()
            saved = mgr.list_all()
            if not saved:
                self._append_result("⚠️ 票据系统中暂无票据，请先在「工作台」添加票据。")
                return
            lines = []
            for t in saved[:30]:
                lines.append(" ".join(f"{n:02d}" for n in t.front + t.back))
            self.input.setPlainText("\n".join(lines))
            self._append_result(f"✅ 已从票据系统读取 {min(len(saved), 30)} 注。")
        except Exception as e:  # noqa: BLE001
            self._append_result(f"⚠️ 读取票据失败：{e}")

    # ---------- 分析功能 ----------
    def _run_structure(self):
        tickets, lottery = self._get_tickets()
        if not tickets:
            self._need_numbers()
            return
        from engine.lottery_quant.structure import StructureAnalyzer
        r = StructureAnalyzer.analyze(tickets, lottery)
        self._append_result("\n🏷 组合评分\n" + f"评分 {r.total_score}/100 · {r.assessment}\n" + r.disclaimer)

    def _run_probability(self):
        tickets, lottery = self._get_tickets()
        lottery = lottery or "dlt"
        from engine.lottery_quant.probability import dlt_probabilities, ssq_probabilities
        prob = dlt_probabilities() if lottery == "dlt" else ssq_probabilities()
        self._append_result("\n🎲 概率分析\n" + prob.summary_text())

    def _run_simulation(self):
        tickets, lottery = self._get_tickets()
        if not tickets:
            self._need_numbers()
            return
        from engine.lottery_quant.simulation import SimulationEngine
        r = SimulationEngine.simulate(tickets, lottery, trials=20_000, seed=42)
        self._append_result("\n🎰 模拟报告\n" + r.summary_text())

    def _run_risk(self):
        tickets, lottery = self._get_tickets()
        lottery = lottery or "dlt"
        from engine.lottery_quant.risk import RiskEngine
        r = RiskEngine.analyze(cost_per_note=2.0, notes_per_draw=len(tickets) or 1,
                               draws_per_week=3, weeks=52, lottery=lottery,
                               tickets=tickets or None, n_years=60, seed=42)
        self._append_result("\n💰 资金风险\n" + r.summary_text())

    def _run_backtest(self):
        from engine.lottery_quant.backtest import StrategyBacktester
        r = StrategyBacktester.run(periods=120)
        self._append_result("\n📈 策略回测\n" + r.summary_text())

    def _need_numbers(self):
        self._append_result("⚠️ 未解析到有效号码。请粘贴号码（每注 5 前区 + 2 后区）或点击「从票据读取」。")
