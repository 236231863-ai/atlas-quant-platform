from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class NavigationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#1a1a2e;")
        layout = QVBoxLayout(); layout.setContentsMargins(0,20,0,0)
        title = QPushButton("Atlas Quant")
        title.setStyleSheet("color:white;font-size:16px;font-weight:bold;padding:10px 20px;border:none;")
        layout.addWidget(title)
        for name in ["Dashboard","Data Analysis","Strategy Lab","Backtest Center","AI Assistant","Reports"]:
            b = QPushButton(name)
            b.setStyleSheet("color:#ccc;padding:8px 20px;border:none;text-align:left;font-size:14px;")
            layout.addWidget(b)
        layout.addStretch(); self.setLayout(layout)
