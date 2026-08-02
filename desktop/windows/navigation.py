from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class NavigationPanel(QWidget):
    page_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#1a1a2e;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 0)
        title = QPushButton("Atlas Quant")
        title.setStyleSheet(
            "color:white;font-size:16px;font-weight:bold;padding:10px 20px;border:none;"
        )
        layout.addWidget(title)
        self._pages = [
            "数据看板",
            "数据分析",
            "策略实验室",
            "回测中心",
            "AI 助手",
            "研究报告",
            "工作台",
            "量化中心",
        ]
        for name in self._pages:
            b = QPushButton(name)
            b.setStyleSheet(
                "color:#ccc;padding:8px 20px;border:none;text-align:left;font-size:14px;"
            )
            b.clicked.connect(lambda checked=False, n=name: self.page_requested.emit(n))
            layout.addWidget(b)
        layout.addStretch()
        self.setLayout(layout)
