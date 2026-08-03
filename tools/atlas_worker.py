"""Atlas Worker - 后台开奖同步服务（v4.4 P2）。

被 Windows 计划任务（AtlasLiveDrawSync）定时唤起：
  - 智能检查所有彩种（开奖日/过期才检查）
  - 有新期自动同步 + 发布事件
  - 同步一次后退出（计划任务每 30 分钟唤起）

也支持手动运行：python tools/atlas_worker.py [--once|--loop] [--interval N]
"""
from __future__ import annotations

import argparse
import os
import sys
import threading

# 确保能导入 engine/（脚本在 tools/ 下运行）
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "desktop")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def sync_once() -> dict:
    """同步一次所有彩种。"""
    from engine.live_draw import LiveDrawService
    svc = LiveDrawService()
    events = svc.sync_all()
    summary = {"dlt": "ok", "ssq": "ok"}
    for ev in events:
        summary[ev.lottery] = f"{ev.event_type}" + (f":{ev.issue}" if ev.issue else "")
    return summary


def run_loop(interval_seconds: int = 1800) -> None:
    """后台长驻循环（供直接运行 --loop）。"""
    from engine.live_draw import LiveDrawService
    svc = LiveDrawService()
    stop = threading.Event()
    print(f"Atlas Worker 后台同步启动（间隔 {interval_seconds}s，Ctrl+C 退出）")
    try:
        svc.auto_sync_loop(interval_seconds=interval_seconds, stop_event=stop)
    except KeyboardInterrupt:
        print("\nWorker 已停止。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas 后台开奖同步 Worker")
    parser.add_argument("--once", action="store_true", help="同步一次后退出（计划任务模式）")
    parser.add_argument("--loop", action="store_true", help="后台长驻循环")
    parser.add_argument("--interval", type=int, default=1800, help="循环间隔秒数")
    args = parser.parse_args()

    if args.loop:
        run_loop(args.interval)
        return 0
    # 默认/--once：同步一次后退出
    summary = sync_once()
    print(f"[worker] 同步完成: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
