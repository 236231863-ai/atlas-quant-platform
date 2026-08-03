"""桌面通知（v4.1.1 Phase 1）。

用 QSystemTrayIcon 显示 Windows 通知（无第三方依赖）。
点击通知可跳到指定页面。
"""
from PySide6.QtWidgets import QSystemTrayIcon, QApplication
from PySide6.QtGui import QIcon


class ReminderNotifier:
    """开奖提醒桌面通知。"""

    def __init__(self):
        self._tray = None
        self._callback = None

    def _ensure(self):
        if self._tray is None:
            app = QApplication.instance() or QApplication([])
            self._tray = QSystemTrayIcon(QIcon(), app)
            self._tray.setVisible(True)
            self._tray.messageClicked.connect(self._on_click)
        return self._tray

    def set_on_click(self, callback):
        """点击通知回调（如跳转兑奖页）。"""
        self._callback = callback

    def _on_click(self):
        if self._callback:
            self._callback()

    def notify(self, title: str, message: str, timeout_ms: int = 5000) -> bool:
        """显示桌面通知。"""
        try:
            tray = self._ensure()
            if not QSystemTrayIcon.isSystemTrayAvailable():
                return False
            tray.showMessage(title, message, QSystemTrayIcon.Information, timeout_ms)
            return True
        except Exception:
            return False

    def show_draw_reminder(self, message: str) -> bool:
        """开奖提醒（标题固定）。"""
        return self.notify("🔔 Atlas 开奖提醒", message)
