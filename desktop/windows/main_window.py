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

PAGES = [
    "Dashboard",
    "Data Analysis",
    "Strategy Lab",
    "Backtest Center",
    "AI Assistant",
    "Reports",
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atlas Quant Platform v3.6.1")
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

        for page in (
            self.dashboard,
            self.analysis,
            self.strategy,
            self.backtest,
            self.ai,
            self.reports,
        ):
            self.stack.addWidget(page)

        layout.addWidget(self.stack)
        self.nav.page_requested.connect(self.switch_page)
        self.strategy.run_backtest_requested.connect(self._run_backtest_from_strategy)

        # 首次引导后按用户选择跳转（30 秒上手）
        if getattr(self, "_first_run_target", None) == "backtest":
            self.switch_page("Backtest Center")
        elif getattr(self, "_first_run_target", None) == "reports":
            self.switch_page("Reports")

        # 首次使用：自动生成第一份报告（FirstSuccessFlow）
        if getattr(self, "_is_first_run", False):
            self._run_first_success()

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
            self.switch_page("Reports")
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
        self.stack.setCurrentIndex(PAGES.index("Backtest Center"))
        self.backtest.run_strategy(method)
