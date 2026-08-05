"""彩票工作台页面（v3.8.0 P4）。

个人彩票工作台：我的票据 / 手动添加彩票 / 最近报告 / 追号观察 / 偏好 / 量化中心入口（v3.9.0）。
"""
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QTextEdit, QToolButton,
)

from data_loader import load_draws


class WorkbenchPage(QWidget):
    """个人彩票工作台。"""

    quant_requested = Signal()   # v3.9.0：跳转量化中心

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 14, 24, 10)
        root.setSpacing(10)

        # 标题行：标题左侧 + 刷新右侧（减少垂直占用）
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        header = QLabel("🧰 彩票工作台")
        header.setStyleSheet("font-size:20px;font-weight:bold;color:#1a1a2e;")
        top_row.addWidget(header, 1)
        refresh = QPushButton("🔄 刷新")
        refresh.clicked.connect(self._refresh)
        refresh.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:6px 16px;border-radius:6px;}")
        top_row.addWidget(refresh)
        root.addLayout(top_row)

        # 顶部：票据统计 + 累计奖金
        self.stats = QLabel("统计加载中…")
        self.stats.setStyleSheet("background:#eef4ff;border-radius:8px;padding:8px 12px;color:#1e3a8a;font-size:13px;")
        root.addWidget(self.stats)

        # 📥 手动添加彩票（用户需求：桌面手动录入入口，复用 v4.8 导入引擎；可折叠省空间）
        add_frame = QFrame()
        add_frame.setStyleSheet(
            "QFrame{background:#f8fbff;border:1px solid #d8e4ff;border-radius:10px;padding:6px;}")
        add_v = QVBoxLayout(add_frame)
        add_v.setContentsMargins(10, 4, 10, 4)
        add_v.setSpacing(5)

        self.add_toggle = QToolButton()
        self.add_toggle.setText("📥 手动添加彩票 ▶")
        self.add_toggle.setCheckable(True)
        self.add_toggle.setChecked(False)  # 默认收起，给票据表让出空间
        self.add_toggle.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.add_toggle.setStyleSheet(
            "QToolButton{font-weight:bold;font-size:13px;color:#1e3a8a;border:none;background:transparent;text-align:left;}")
        self.add_toggle.clicked.connect(self._toggle_add)
        add_v.addWidget(self.add_toggle)

        self.add_body = QWidget()
        body = QVBoxLayout(self.add_body)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(5)

        cfg_row = QHBoxLayout()
        cfg_row.setSpacing(8)
        cfg_row.addWidget(QLabel("彩种"))
        self.lottery_combo = QComboBox()
        self.lottery_combo.addItem("大乐透", "dlt")
        self.lottery_combo.addItem("双色球", "ssq")
        self.lottery_combo.setStyleSheet(
            "QComboBox{padding:3px 10px;border:1px solid #cfe0ff;border-radius:6px;background:white;}")
        cfg_row.addWidget(self.lottery_combo)
        cfg_row.addWidget(QLabel("购买日期"))
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("YYYY-MM-DD（留空=今天）")
        self.date_edit.setStyleSheet(
            "QLineEdit{padding:3px 8px;border:1px solid #cfe0ff;border-radius:6px;background:white;}")
        self.date_edit.setFixedWidth(200)
        cfg_row.addWidget(self.date_edit)
        cfg_row.addStretch()
        body.addLayout(cfg_row)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("每行一组，例如：01 05 12 23 30 + 06 08（可粘贴多行）")
        self.input_edit.setFixedHeight(52)
        self.input_edit.setStyleSheet(
            "QTextEdit{background:white;border:1px solid #cfe0ff;border-radius:6px;"
            "font-size:12px;padding:4px 6px;}")
        body.addWidget(self.input_edit)

        add_btn_row = QHBoxLayout()
        add_btn_row.setSpacing(8)
        self.add_btn = QPushButton("➕ 添加")
        self.add_btn.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:5px 18px;"
            "border-radius:6px;font-weight:bold;font-size:12px;}")
        self.add_btn.clicked.connect(self._manual_add)
        add_btn_row.addWidget(self.add_btn)
        self.add_result = QLabel("")
        self.add_result.setWordWrap(True)
        self.add_result.setStyleSheet("color:#2e7d32;font-size:12px;")
        add_btn_row.addWidget(self.add_result, 1)
        body.addLayout(add_btn_row)
        add_v.addWidget(self.add_body)
        root.addWidget(add_frame)
        self._toggle_add()  # 初始化收起/展开状态（默认收起）

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
        root.addWidget(self.ticket_table, 3)

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

        # 🎯 彩票量化分析入口（v3.9.0 Phase 8）
        quant_btn = QPushButton("🎯 彩票量化分析")
        quant_btn.setStyleSheet(
            "QPushButton{background:linear-gradient(90deg,#2a6df4,#6a4df4);color:white;border:none;"
            "padding:12px 20px;border-radius:8px;font-size:14px;font-weight:bold;}"
            "QPushButton:hover{background:#1e56c8;}"
        )
        quant_btn.clicked.connect(self.quant_requested.emit)
        root.addWidget(quant_btn)

        self._refresh()

    def _toggle_add(self) -> None:
        """展开/收起手动添加面板。"""
        visible = self.add_toggle.isChecked()
        self.add_body.setVisible(visible)
        self.add_toggle.setText("📥 手动添加彩票 ▼" if visible else "📥 手动添加彩票 ▶")

    def _manual_add(self) -> None:
        """手动添加彩票：复用 TextImporter 解析并写入票据库。"""
        from engine.import_center import TextImporter
        text = self.input_edit.toPlainText().strip()
        if not text:
            self.add_result.setStyleSheet("color:#c62828;font-size:12px;")
            self.add_result.setText("⚠️ 请输入号码")
            return
        lottery = self.lottery_combo.currentData()
        buy_date = self.date_edit.text().strip()
        rep = TextImporter.import_text(text, lottery=lottery, buy_date=buy_date)
        if rep.total_imported > 0:
            self.input_edit.clear()
            self.add_result.setStyleSheet("color:#2e7d32;font-size:12px;")
            self.add_result.setText(rep.summary_text())
            self._refresh()
        else:
            self.add_result.setStyleSheet("color:#c62828;font-size:12px;")
            self.add_result.setText("⚠️ 没有成功添加（号码格式不正确）")

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
