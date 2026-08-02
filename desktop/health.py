"""Atlas 产品稳定性模块（v3.6.1 Phase 5）。

提供：
  - Global Exception Handler : 全局未捕获异常写入日志
  - Crash Recovery           : 异常退出标记检测 + 恢复提示
  - Log Export               : 日志落盘 ~/.atlas/logs/ 并支持导出
  - Health Check             : 启动健康检查（数据/依赖/目录）
"""
from __future__ import annotations

import logging
import os
import shutil
import sys
import traceback
from datetime import datetime
from typing import List, Optional

from PySide6.QtWidgets import QMessageBox

APP_DIR_NAME = ".atlas"
LOG_DIR = "logs"
CRASH_MARK = ".crash_mark"

logger = logging.getLogger("atlas")


def _atlas_dir() -> str:
    home = os.path.expanduser("~")
    d = os.path.join(home, APP_DIR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _log_dir() -> str:
    d = os.path.join(_atlas_dir(), LOG_DIR)
    os.makedirs(d, exist_ok=True)
    return d


def _crash_mark_path() -> str:
    return os.path.join(_atlas_dir(), CRASH_MARK)


# ---------------- 日志 ----------------
def setup_logging() -> str:
    """配置日志：控制台 + 滚动文件，返回日志目录。"""
    log_dir = _log_dir()
    log_file = os.path.join(log_dir, f"atlas_{datetime.now():%Y%m%d}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    logger.info("Atlas 启动，日志文件: %s", log_file)
    return log_dir


# ---------------- 全局异常 ----------------
def install_excepthook() -> None:
    """安装全局未捕获异常处理器：写日志 + 标记崩溃。"""

    def _hook(exc_type, exc_value, exc_tb):
        text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.critical("未捕获异常:\n%s", text)
        mark_crash()
        # 原样打印，避免吞掉 PyInstaller 的错误弹窗
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


# ---------------- 崩溃恢复 ----------------
def mark_crash() -> None:
    """记录一次崩溃（下次启动可感知）。"""
    try:
        with open(_crash_mark_path(), "w", encoding="utf-8") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except OSError:
        pass


def clear_crash_mark() -> None:
    """正常退出时清除崩溃标记。"""
    try:
        if os.path.exists(_crash_mark_path()):
            os.remove(_crash_mark_path())
    except OSError:
        pass


def was_crashed() -> Optional[str]:
    """上次是否异常退出；若是返回崩溃时间字符串。"""
    p = _crash_mark_path()
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                return f.read().strip() or "未知时间"
        except OSError:
            return "未知时间"
    return None


def show_crash_recovery_dialog(parent=None) -> bool:
    """若上次异常退出，弹出恢复提示。返回是否检测到崩溃。"""
    when = was_crashed()
    if not when:
        return False
    log_dir = _log_dir()
    box = QMessageBox(parent)
    box.setWindowTitle("Atlas 恢复提示")
    box.setIcon(QMessageBox.Information)
    box.setText(f"检测到上次异常退出（{when}）。\n运行日志已保存，可协助排查问题。")
    box.setInformativeText(f"日志目录：{log_dir}\n\n点击「继续使用」正常启动。")
    box.setStandardButtons(QMessageBox.Ok)
    box.exec()
    clear_crash_mark()
    return True


# ---------------- 日志导出 ----------------
def export_logs(target_dir: str) -> List[str]:
    """复制日志文件到目标目录，返回复制文件路径列表。"""
    log_dir = _log_dir()
    exported: List[str] = []
    os.makedirs(target_dir, exist_ok=True)
    for fn in os.listdir(log_dir):
        if fn.endswith(".log"):
            src = os.path.join(log_dir, fn)
            dst = os.path.join(target_dir, fn)
            try:
                shutil.copy2(src, dst)
                exported.append(dst)
            except OSError:
                continue
    return exported


# ---------------- 健康检查 ----------------
def check_health(data_total: Optional[int] = None) -> List[str]:
    """启动健康检查，返回问题列表（空 = 健康）。"""
    issues: List[str] = []

    # 1. 数据量
    if data_total is not None and data_total < 50:
        issues.append(f"数据量偏少（{data_total} 期），统计结论可能不稳健。")

    # 2. 关键目录可写
    try:
        os.makedirs(_log_dir(), exist_ok=True)
    except OSError:
        issues.append("无法写入日志目录，请检查 ~/.atlas 权限。")

    # 3. 依赖
    for mod, name in [("PySide6", "PySide6"), ("matplotlib", "matplotlib"), ("fpdf", "fpdf2")]:
        try:
            __import__(mod)
        except ImportError:
            issues.append(f"缺少依赖 {name}，部分功能不可用。")

    return issues
