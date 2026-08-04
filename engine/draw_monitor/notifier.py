"""draw_monitor.notifier - Windows 后台提醒（v4.5 P3）。

解决「必须打开软件才能提醒」：
  Windows Toast Notification（无需软件运行）+ 降级链
  开奖提醒 / 中奖提醒 / 待兑奖提醒

通知通道（按优先级）：
  1. PowerShell Toast（Windows 原生通知）
  2. msg.exe（登录会话消息框）
  3. 通知日志文件（~/.atlas/notifications.jsonl，兜底可查）

worker 在后台同步后调用 notify_draw_event 发出提醒。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List, Optional


class WindowsNotifier:
    """Windows 通知器（后台可用）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")

    # ---------- 通知通道 ----------
    def notify_toast(self, title: str, message: str) -> bool:
        """PowerShell Windows Toast 通知。"""
        if sys.platform != "win32":
            return False
        # 转义单引号
        title_s = title.replace("'", "''")
        msg_s = message.replace("'", "''")
        ps = (
            "$ErrorActionPreference='SilentlyContinue';"
            "try{"
            "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;"
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
            "$n=$t.GetElementsByTagName('text');"
            f"$n.Item(0).AppendChild($t.CreateTextNode('{title_s}'))|Out-Null;"
            f"$n.Item(1).AppendChild($t.CreateTextNode('{msg_s}'))|Out-Null;"
            "$toast=[Windows.UI.Notifications.ToastNotification]::new($t);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Atlas').Show($toast);"
            "Write-Output 'OK'}catch{Write-Output ('ERR:'+$_.Exception.Message)}"
        )
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True, text=True, timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return "OK" in (r.stdout or "")
        except Exception:
            return False

    def notify_msg(self, title: str, message: str) -> bool:
        """msg.exe 登录会话消息框。"""
        if sys.platform != "win32":
            return False
        try:
            r = subprocess.run(
                ["msg", "*", f"/TIME:30", f"{title}: {message}"],
                capture_output=True, text=True, timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return r.returncode == 0
        except Exception:
            return False

    def notify_log(self, kind: str, title: str, message: str) -> bool:
        """写通知日志（兜底可查）。"""
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            path = os.path.join(self.storage_dir, "notifications.jsonl")
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "kind": kind, "title": title, "message": message,
                }, ensure_ascii=False) + "\n")
            return True
        except OSError:
            return False

    # ---------- 统一入口 ----------
    def notify(self, title: str, message: str, kind: str = "reminder") -> dict:
        """发送通知，返回各通道结果。"""
        result = {"toast": False, "msg": False, "log": True}
        result["log"] = self.notify_log(kind, title, message)
        # 优先 Toast，降级 msg
        if self.notify_toast(title, message):
            result["toast"] = True
        elif self.notify_msg(title, message):
            result["msg"] = True
        return result

    # ---------- 便捷：开奖/中奖/待兑奖 ----------
    def notify_draw_reminder(self, lottery_name: str, issue: str = "",
                             pending: int = 0) -> dict:
        title = f"🔔 {lottery_name}开奖提醒"
        msg = f"{lottery_name}最新开奖：{issue or '已更新'}"
        if pending:
            msg += f" · {pending} 张待兑奖"
        return self.notify(title, msg, kind="draw_reminder_received")

    def notify_win(self, lottery_name: str, won: int,
                   amount: float, issue: str = "") -> dict:
        title = f"🎉 {lottery_name}中奖提醒"
        msg = f"你的彩票中奖 {won} 注 ¥{amount:,.0f}" + (f"（{issue}期）" if issue else "")
        return self.notify(title, msg, kind="win")

    def notify_pending(self, lottery_name: str, pending: int) -> dict:
        title = f"🧾 {lottery_name}待兑奖提醒"
        msg = f"你有 {pending} 张彩票已开奖待兑奖，打开 Atlas 查看结果"
        return self.notify(title, msg, kind="pending_claim")


def notify_draw_event(event) -> dict:
    """draw_updated 事件 → 后台提醒。"""
    n = WindowsNotifier()
    return n.notify_draw_reminder(event.lottery_name, event.issue)
