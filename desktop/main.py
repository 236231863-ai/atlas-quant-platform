"""Atlas Quant Desktop Client"""
import sys
from PySide6.QtWidgets import QApplication
from desktop.windows.main_window import MainWindow
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Atlas Quant Platform")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__": main()
