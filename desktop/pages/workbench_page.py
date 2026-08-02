"""彩票工作台页面（v3.8.0 P4）。

个人彩票工作台：我的票据 / 最近报告 / 追号观察 / 偏好。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)

from data_loader import load_draws


class WorkbenchPage(QWidget):
    """个人彩票工作台。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        header = QLabel("🧰 彩票工作台")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        # 顶部：票据统计 + 累计奖金
        self.stats = QLabel("统计加载中…")
        self.stats.setStyleSheet("background:#eef4ff;border-radius:8px;padding:12px;color:#1e3a8a;font-size:13px;")
        root.addWidget(self.stats)

        refresh = QPushButton("🔄 刷新")
        refresh.clicked.connect(self._refresh)
        refresh.setStyleSheet("QPushButton{background:#2a6df4;color:white;border:none;padding:8px 16px;border-radius:6px;}")
        root.addWidget(refresh)

        # 票据表
        root.addWidget(QLabel("我的票据"))
        self.ticket_table = QTableWidget(0, 6)
        self.ticket_table.setHorizontalHeaderLabels(["编号", "彩种", "号码", "购买", "开奖", "保存时间"])
        self.ticket_table.verticalHeader().setVisible(False)
        self.ticket_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ticket_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.ticket_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ticket_table.setStyleSheet("QTableWidget{font-size:12px;border:1px solid #e8ecf2;border-radius:8px;}"
                                        "QHeaderView::section{background:#f4f6fa;border:none;padding:6px;}")
        root.addWidget(self.ticket_table, 1)

        # 追号观察 + 最近报告
        row = QHBoxLayout()
        self.chase = QLabel("追号加载中…")
        self.chase.setWordWrap(True)
        self.chase.setStyleSheet("background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.chase, 1)
        self.reports = QLabel("报告加载中…")
        self.reports.setWordWrap(True)
        self.reports.setStyleSheet("background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.reports, 1)
        root.addLayout(row)

        # 产品概览（决策层入口，v3.8.0 原则整改）
        self.overview = QLabel("产品概览加载中…")
        self.overview.setWordWrap(True)
        self.overview.setStyleSheet("background:#fff8ee;border-radius:8px;border:1px solid #f0e0c0;padding:10px;color:#7a5c1e;font-size:12px;")
        root.addWidget(self.overview)

        self._refresh()

    def _refresh(self):
        try:
            from engine.ticket_system import TicketManager
            from engine.report_center import ReportCenter
            from engine.chase_analysis import ChaseAnalysis
            from engine.user_memory import UserMemory

            tm = TicketManager()
            rc = ReportCenter()
            mem = UserMemory()
            draws = load_draws(mem.preferred_lottery())

            self.stats.setText(
                f"📦 票据 {tm.count()} 张 · 🏆 累计奖金 ¥{rc.total_winnings():,.0f} · "
                f"偏好彩种 {mem.preferred_lottery()}"
            )
            # 票据表
            tickets = tm.list_all()
            self.ticket_table.setRowCount(len(tickets))
            for r, t in enumerate(tickets):
                vals = [t.ticket_id, t.lottery,
                        " ".join(f"{n:02d}" for n in t.front) + " + " + " ".join(f"{n:02d}" for n in t.back),
                        t.buy_date or "-", t.draw_date or "-", t.saved_at]
                for c, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(0x0004 | 0x0080)
                    self.ticket_table.setItem(r, c, item)
            # 追号
            self.chase.setText(ChaseAnalysis.summary(draws) if draws else "暂无数据")
            # 最近报告
            reports = rc.list_all()[:3]
            if reports:
                lines = ["📄 最近报告"]
                for r in reports:
                    lines.append(f"· {r.report_id} {r.lottery} 中{r.won_notes}/{r.tickets} ¥{r.total:,.0f}")
                self.reports.setText("\n".join(lines))
            else:
                self.reports.setText("📄 暂无兑奖报告（在 AI 助手输入号码兑奖后自动保存）")
            # 产品概览（决策层入口）
            try:
                from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary
                from engine.intelligence.product_director_v2 import ProductDirectorV2
                from backend.feedback import FeedbackManager
                ui = UserIntelligenceV3()
                s = build_behavior_summary(ui)
                fb = [{"content": f.content, "status": f.status} for f in FeedbackManager().list_all()]
                ass = ProductDirectorV2.assess(
                    total_events=s.total_events, active_days=s.active_days,
                    analysis_runs=s.by_event.get("ANALYSIS_RUN", 0),
                    backtest_runs=s.by_event.get("BACKTEST_RUN", 0),
                    exports=s.by_event.get("REPORT_EXPORT", 0),
                    feedback_count=s.by_event.get("FEEDBACK_SEND", 0),
                    feedback_items=fb,
                )
                lines = ["🏢 产品概览"]
                lines.append(f"· 健康分 {ass.health_score:.0f}/100 · 用户价值 {ass.user_value.total:.0f}（{ass.user_value.level}）")
                for issue in ass.issues[:2]:
                    lines.append(f"· ⚠ {issue}")
                for rcmd in ass.roadmap[:2]:
                    lines.append(f"· → {rcmd}")
                self.overview.setText("\n".join(lines))
            except Exception:
                self.overview.setText("🏢 产品概览暂不可用")
        except Exception as e:
            self.stats.setText(f"工作台加载异常：{e}")
