"""Atlas Quant Desktop Client"""
import sys

from PySide6.QtWidgets import QApplication

import health
from windows.main_window import MainWindow

# 单实例锁名称（v4.9.1 修复：多实例并发访问同一数据库导致未响应）
_SINGLE_INSTANCE_KEY = "atlas_quant_single_instance"


def _is_already_running() -> bool:
    """探测是否已有 Atlas 实例在运行。"""
    from PySide6.QtNetwork import QLocalSocket

    probe = QLocalSocket()
    probe.connectToServer(_SINGLE_INSTANCE_KEY)
    if probe.waitForConnected(300):
        # 已有实例：发送唤醒信号（主实例收到后聚焦窗口）
        try:
            probe.write(b"show")
            probe.flush()
            probe.waitForBytesWritten(200)
        except Exception:
            pass
        probe.disconnectFromServer()
        return True
    return False


def main():
    # 稳定性：日志 + 全局异常 + 崩溃恢复（v3.6.1 Phase 5）
    health.setup_logging()
    health.install_excepthook()

    app = QApplication(sys.argv)
    app.setApplicationName("Atlas Quant Platform")

    # 单实例保护（v4.9.1）：已有实例则聚焦并退出，避免多实例堆积
    from PySide6.QtNetwork import QLocalServer

    if _is_already_running():
        print("Atlas 已在运行，聚焦已有窗口", file=sys.stderr)
        sys.exit(0)

    server = QLocalServer()
    server.removeServer(_SINGLE_INSTANCE_KEY)  # 清理崩溃残留
    if not server.listen(_SINGLE_INSTANCE_KEY):
        print("单实例启动失败，退出", file=sys.stderr)
        sys.exit(1)

    window = MainWindow()

    def _focus_existing():
        try:
            window.show()
            window.raise_()
            window.activateWindow()
        except Exception:
            pass

    server.newConnection.connect(_focus_existing)

    window.show()
    code = app.exec()
    health.clear_crash_mark()  # 正常退出，清除崩溃标记
    sys.exit(code)


if __name__ == "__main__":
    main()
