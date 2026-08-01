from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from windows.navigation import NavigationPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atlas Quant Platform v0.7.0")
        self.setMinimumSize(1200, 800)
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central); layout.setContentsMargins(0,0,0,0)
        self.nav = NavigationPanel(self); self.nav.setFixedWidth(240)
        layout.addWidget(self.nav)
        content = QWidget(); cl = QVBoxLayout(content); cl.setContentsMargins(24,24,24,24)
        cl.addWidget(QLabel("Dashboard")); cl.addWidget(QLabel("System Online"))
        cl.addStretch(); layout.addWidget(content)
