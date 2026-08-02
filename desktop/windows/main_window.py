from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
)
from windows.navigation import NavigationPanel

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
        self.setWindowTitle("Atlas Quant Platform v3.6.0")
        self.setMinimumSize(1200, 800)
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

    def switch_page(self, name: str) -> None:
        if name in PAGES:
            self.stack.setCurrentIndex(PAGES.index(name))

    def _run_backtest_from_strategy(self, method: str) -> None:
        self.stack.setCurrentIndex(PAGES.index("Backtest Center"))
        self.backtest.run_strategy(method)
