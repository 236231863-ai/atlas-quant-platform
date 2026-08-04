import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
)
from windows.navigation import NavigationPanel

from user_profile import load_profile, save_profile
from pages.dashboard_page import DashboardPage
from pages.analysis_page import AnalysisPage
from pages.strategy_page import StrategyPage
from pages.backtest_page import BacktestPage
from pages.ai_page import AIPage
from pages.reports_page import ReportsPage
from pages.workbench_page import WorkbenchPage
from pages.quant_page import QuantPage
from pages.profile_page import ProfilePage

PAGES = [
    "数据看板",
    "数据分析",
    "策略实验室",
    "回测中心",
    "AI 助手",
    "研究报告",
    "工作台",
    "量化中心",
    "个人中心",
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atlas Quant Platform v4.6.0")
        self.setWindowIcon(self._load_icon())
        self.setMinimumSize(1200, 800)
        self._run_first_run_if_needed()
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.nav = NavigationPanel(self)
        self.nav.setFixedWidth(240)
        layout.addWidget(self.nav)

        self.stack = QStackedWidget()
        self.dashboard = DashboardPage()
        self.analysis = AnalysisPage()
        self.strategy = StrategyPage()
        self.backtest = BacktestPage()
        self.ai = AIPage()
        self.reports = ReportsPage()
        self.workbench = WorkbenchPage()
        self.quant = QuantPage()
        self.profile = ProfilePage()

        for page in (
            self.dashboard,
            self.analysis,
            self.strategy,
            self.backtest,
            self.ai,
            self.reports,
            self.workbench,
            self.quant,
            self.profile,
        ):
            self.stack.addWidget(page)

        layout.addWidget(self.stack)
        self.nav.page_requested.connect(self.switch_page)
        self.strategy.run_backtest_requested.connect(self._run_backtest_from_strategy)
        self.workbench.quant_requested.connect(lambda: self.switch_page("量化中心"))

        # 首次引导后按用户选择跳转（30 秒上手）
        if getattr(self, "_first_run_target", None) == "backtest":
            self.switch_page("回测中心")
        elif getattr(self, "_first_run_target", None) == "reports":
            self.switch_page("研究报告")

        # 首次使用：自动生成第一份报告（FirstSuccessFlow）
        if getattr(self, "_is_first_run", False):
            self._run_first_success()

        # 帮助中心（v3.7.1 Phase 5）
        help_action = self.menuBar().addAction("🆘 帮助")
        help_action.triggered.connect(self._open_help)

        # 行为事件（v3.8.0 Phase 1）+ v4.3 用户行为事件
        try:
            from engine.user_intelligence.v3 import UserIntelligenceV3
            UserIntelligenceV3().app_start()
        except Exception:
            pass
        try:
            from engine.user_events import EventTracker
            EventTracker().record("app_opened", {"source": "launch"})
        except Exception:
            pass

        # v4.3.1：启动时后台静默更新开奖数据（不阻塞 UI，无网静默降级）
        try:
            import threading
            from data_loader import maybe_update_draws
            for lot in ("dlt", "ssq"):
                threading.Thread(target=maybe_update_draws,
                                 kwargs={"lottery": lot},
                                 daemon=True).start()
        except Exception:
            pass

        # v4.1.1 Phase 1：开奖桌面通知（启动时提醒；v4.3 记录用户提醒事件）
        try:
            from pages.reminder_notifier import ReminderNotifier
            from engine.ticket_system import TicketManager
            from engine.reminder_center import today_reminders, ReminderEngine
            self.notifier = ReminderNotifier()
            self.notifier.set_on_click(lambda: self.switch_page("AI 助手"))
            tickets = [t.__dict__ for t in TicketManager().list_all()]
            r = today_reminders(tickets)
            if r.draw_today or r.prize_due > 0 or r.unclaimed > 0:
                ReminderEngine.notify_and_record(
                    self.notifier, "🔔 Atlas 开奖提醒", r.notify_text())
        except Exception:
            pass

        # v4.3 P2：自动兑奖中心（开奖后自动匹配票据 → 通知 → 记录 auto_claim_run 事件）
        try:
            from engine.claim_center import ClaimCenter
            for lottery in ("dlt", "ssq"):
                rep = ClaimCenter.auto_claim(tickets, lottery=lottery,
                                             notifier=self.notifier)
        except Exception:
            pass

    def _open_help(self) -> None:
        """打开帮助中心。"""
        try:
            from pages.help_dialog import HelpDialog
            HelpDialog(self).exec()
        except Exception:
            pass

    def _run_first_success(self) -> None:
        """首次成功体验：自动生成报告 + 保存历史 + 解锁成就（v3.7.0）。"""
        try:
            from engine.onboarding import (
                FirstSuccessFlow, default_report_generator,
                default_history_saver, UserAchievement,
            )
            from data_loader import load_draws

            lottery = getattr(self.profile, "data_lottery", "dlt")
            draws = load_draws(lottery)
            flow = FirstSuccessFlow(lottery=lottery)
            flow.register("generate_report", default_report_generator(draws))
            saver = default_history_saver()
            flow.register("save_history", lambda: saver(flow.result.get("generate_report")))
            flow.run_all()
            report = flow.result.get("generate_report") or {}
            if report and report.get("lines"):
                self.reports.show_report(report)
            # 成就
            ach = UserAchievement().load()
            ach.unlock("first_analysis")
            ach.unlock("first_report")
            if len(draws) >= 500:
                ach.unlock("data_500")
            self.switch_page("研究报告")
        except Exception:
            # 首次成功体验失败不影响使用
            pass

    def _run_first_run_if_needed(self) -> None:
        """首次启动显示引导对话框并保存用户档案。"""
        self.profile = load_profile()
        # 崩溃恢复提示（v3.6.1 Phase 5）
        try:
            from health import show_crash_recovery_dialog
            show_crash_recovery_dialog(self)
        except Exception:
            pass
        if not self.profile.first_run_completed:
            from pages.first_run_dialog import FirstRunDialog

            dlg = FirstRunDialog(self.profile, self)
            dlg.exec()
            # 记录引导选择：用途=backtest/reports 时跳对应页，其余到 Dashboard
            self._first_run_target = (
                "backtest" if dlg.purpose == "backtest" or dlg.mode == "backtest"
                else ("reports" if dlg.purpose == "reports" else "dashboard")
            )
            self._is_first_run = True
            self.profile = load_profile()

    def _load_icon(self) -> QIcon:
        """加载品牌图标（打包后从 sys._MEIPASS 定位）。"""
        base = getattr(os.sys, "_MEIPASS", None)
        candidates = []
        if base:
            candidates.append(os.path.join(base, "branding", "logo.ico"))
        candidates.extend(
            [
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "branding", "logo.ico"),
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "branding", "icon.ico"),
            ]
        )
        for p in candidates:
            if os.path.exists(p):
                return QIcon(p)
        return QIcon()

    def switch_page(self, name: str) -> None:
        if name in PAGES:
            self.stack.setCurrentIndex(PAGES.index(name))
            # 用户行为追踪（v3.7.0 Phase 4）
            try:
                from engine.user_feedback_v2 import UserFeedbackTracker
                UserFeedbackTracker().page_view(name)
            except Exception:
                pass

    def _run_backtest_from_strategy(self, method: str) -> None:
        self.stack.setCurrentIndex(PAGES.index("回测中心"))
        self.backtest.run_strategy(method)
