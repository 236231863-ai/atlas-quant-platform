"""Atlas Quant Desktop Client"""
import sys

from PySide6.QtWidgets import QApplication

import health
from windows.main_window import MainWindow


def main():
    # 稳定性：日志 + 全局异常 + 崩溃恢复（v3.6.1 Phase 5）
    health.setup_logging()
    health.install_excepthook()

    app = QApplication(sys.argv)
    app.setApplicationName("Atlas Quant Platform")
    window = MainWindow()
    window.show()
    code = app.exec()
    health.clear_crash_mark()  # 正常退出，清除崩溃标记
    sys.exit(code)


if __name__ == "__main__":
    main()
