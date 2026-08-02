"""个人中心页面（v4.0.0 Phase 6）。

展示：我的票据 / 我的投入 / 我的中奖 / 我的风险 / 我的报告 / 我的趋势。
桌面必须可见。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)

from data_loader import load_draws


class ProfilePage(QWidget):
    """个人中心：个人决策智能面板。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QLabel("👤 个人中心")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        sub = QLabel("我的票据 · 投入 · 中奖 · 风险 · 报告 · 趋势")
        sub.setStyleSheet("color:#666;font-size:12px;")
        root.addWidget(sub)

        refresh = QPushButton("🔄 刷新")
        refresh.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 16px;border-radius:6px;}"
        )
        refresh.clicked.connect(self._refresh)
        root.addWidget(refresh)

        # 统计卡片区（我的票据/投入/中奖/风险）
        cards = QHBoxLayout()
        cards.setSpacing(10)
        self.ticket_card = self._card("我的票据")
        self.spend_card = self._card("我的投入")
        self.win_card = self._card("我的中奖")
        self.risk_card = self._card("我的风险")
        for c in (self.ticket_card, self.spend_card, self.win_card, self.risk_card):
            cards.addWidget(c)
        root.addLayout(cards)

        # 我的报告 + 趋势
        row = QHBoxLayout()
        row.setSpacing(10)
        self.report_area = QLabel("报告加载中…")
        self.report_area.setWordWrap(True)
        self.report_area.setStyleSheet(
            "background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.report_area, 1)

        self.trend_area = QLabel("趋势加载中…")
        self.trend_area.setWordWrap(True)
        self.trend_area.setStyleSheet(
            "background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.trend_area, 1)
        root.addLayout(row, 1)

        self.disclaimer = QLabel("⚠️ 彩票开奖结果具有随机性。本中心帮助你了解投注行为并管理风险，不涉及预测。")
        self.disclaimer.setWordWrap(True)
        self.disclaimer.setStyleSheet("color:#8a6d1a;font-size:11px;")
        root.addWidget(self.disclaimer)

        self._refresh()

    def _card(self, title):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:white;border-radius:8px;border:1px solid #e8ecf2;padding:8px;}")
        v = QVBoxLayout(frame)
        v.setContentsMargins(8, 8, 8, 8)
        label = QLabel(title)
        label.setStyleSheet("font-weight:bold;font-size:12px;color:#1a1a2e;")
        value = QLabel("—")
        value.setStyleSheet("font-size:18px;font-weight:bold;color:#2a6df4;")
        v.addWidget(label)
        v.addWidget(value)
        frame.value_label = value
        return frame

    def _refresh(self):
        """刷新个人数据。"""
        try:
            from engine.ticket_system import TicketManager
            from engine.user_behavior import analyze_behavior
            from engine.personal_review import PersonalReviewEngine
            from engine.budget_manager import BudgetPlanner

            tm = TicketManager()
            tickets = [t.__dict__ for t in tm.list_all()]

            # 我的票据
            self.ticket_card.value_label.setText(str(len(tickets)))

            if not tickets:
                self.spend_card.value_label.setText("¥0")
                self.win_card.value_label.setText("¥0")
                self.risk_card.value_label.setText("—")
                self.report_area.setText("暂无投注数据。请到「工作台」添加票据后查看个人分析。")
                self.trend_area.setText("暂无趋势数据。")
                return

            # 我的投入 / 行为
            bh = analyze_behavior(tickets)
            self.spend_card.value_label.setText(f"¥{bh.total_spent:,.0f}")
            self.risk_card.value_label.setText(bh.risk_level)

            # 我的中奖 / 复盘
            rv = PersonalReviewEngine.review(tickets)
            self.win_card.value_label.setText(f"¥{rv.total_winnings:,.0f}")

            # 我的报告
            self.report_area.setText(
                f"📋 复盘报告\n"
                f"· 总投入：¥{rv.total_investment:,.0f}\n"
                f"· 总中奖：¥{rv.total_winnings:,.0f}\n"
                f"· 净收益：¥{rv.net_profit:,.0f}\n"
                f"· 中奖率：{rv.win_rate * 100:.1f}%\n"
                f"· 最高投入：{rv.peak_month or '—'}"
            )

            # 我的趋势
            trend = "📈 月度投入趋势\n"
            if bh.monthly_avg:
                trend += f"· 月均投入：¥{bh.monthly_avg:,.0f}\n"
                trend += f"· 年投入外推：¥{bh.annual_projection:,.0f}\n"
                trend += f"· 追号次数：{bh.chase_count}\n"
                trend += f"· 高频月份：{bh.peak_month}\n"
                trend += f"· 行为风险等级：{bh.risk_level}"
            else:
                trend += "· 暂无足够日期数据"
            self.trend_area.setText(trend)

            # 预算健康
            try:
                bp = BudgetPlanner()
                b = bp.evaluate_tickets(tickets)
                self.report_area.setText(self.report_area.text() + f"\n· 预算健康度：{b.health_score}/100")
            except Exception:
                pass
        except Exception as e:  # noqa: BLE001
            self.report_area.setText(f"加载失败：{e}")
