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
        except Exception as e:
            self.stats.setText(f"工作台加载异常：{e}")
