"""live_draw.background - Atlas Background Service（v4.4 P2）。

Windows 后台开奖同步服务：
  - 软件关闭仍可运行（独立计划任务）
  - 定时检查开奖（每 30 分钟唤起 worker）
  - 支持开机启动（计划任务 + 开机启动触发器）
  - 提供 安装 / 卸载 / 状态查询

实现：schtasks 创建计划任务 → 定时运行 tools/atlas_worker.py（同步一次后退出）。
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional

TASK_NAME = "AtlasLiveDrawSync"
TASK_PATH = f"Atlas\\{TASK_NAME}"
DEFAULT_INTERVAL_MINUTES = 30


def _worker_script() -> str:
    """返回 worker 脚本路径。"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(root, "tools", "atlas_worker.py")


def _run(cmd: list) -> subprocess.CompletedProcess:
    """运行命令（隐藏窗口）。"""
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return subprocess.run(cmd, capture_output=True, text=True,
                              creationflags=creationflags, timeout=30)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


class BackgroundServiceManager:
    """Windows 计划任务后台服务管理。"""

    @classmethod
    def install(cls, interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
                on_startup: bool = True) -> dict:
        """安装计划任务：定时运行 worker。

        返回 {ok, task, detail}。失败返回 ok=False + detail。
        """
        py = sys.executable
        worker = _worker_script()
        if not os.path.exists(worker):
            return {"ok": False, "task": TASK_PATH, "detail": f"worker 不存在: {worker}"}
        tr = f'"{py}" "{worker}"'
        # 每 interval 分钟运行
        r = _run(["schtasks", "/Create", "/TN", TASK_PATH, "/TR", tr,
                  "/SC", "MINUTE", "/MO", str(interval_minutes), "/F"])
        detail = (r.stdout or "").strip() or (r.stderr or "").strip()
        if r.returncode != 0:
            return {"ok": False, "task": TASK_PATH, "detail": detail}
        # 开机启动触发（额外触发器）
        if on_startup:
            _run(["schtasks", "/Create", "/TN", TASK_PATH + "Boot",
                  "/TR", tr, "/SC", "ONSTART", "/F"])
        return {"ok": True, "task": TASK_PATH, "detail": detail or "installed"}

    @classmethod
    def uninstall(cls) -> dict:
        """卸载计划任务。"""
        r1 = _run(["schtasks", "/Delete", "/TN", TASK_PATH, "/F"])
        r2 = _run(["schtasks", "/Delete", "/TN", TASK_PATH + "Boot", "/F"])
        ok = r1.returncode == 0 or r2.returncode == 0
        return {"ok": ok, "task": TASK_PATH,
                "detail": (r1.stdout or r2.stdout or "removed").strip()}

    @classmethod
    def status(cls) -> dict:
        """查询服务状态。"""
        r = _run(["schtasks", "/Query", "/TN", TASK_PATH])
        exists = r.returncode == 0
        boot_exists = _run(["schtasks", "/Query", "/TN", TASK_PATH + "Boot"]).returncode == 0
        state = "installed"
        if exists and "Running" in (r.stdout or ""):
            state = "running"
        return {"installed": exists, "boot_on_startup": boot_exists,
                "state": state if exists else "not_installed",
                "task": TASK_PATH}


def service_cli(action: str) -> dict:
    """CLI 入口：install / uninstall / status。"""
    if action == "install":
        return BackgroundServiceManager.install()
    if action == "uninstall":
        return BackgroundServiceManager.uninstall()
    if action == "status":
        return BackgroundServiceManager.status()
    return {"ok": False, "detail": f"未知操作: {action}"}
