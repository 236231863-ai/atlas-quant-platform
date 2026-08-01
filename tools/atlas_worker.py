"""Atlas Worker - background service entry point.

打包为 Atlas_Worker.exe 的后台服务入口。
职责：数据缓存刷新循环，可独立运行，Ctrl+C 安全退出。
"""
from __future__ import annotations

import sys
import time
from typing import Optional


def _refresh_data() -> bool:
    """刷新本地数据缓存（当前为验证性实现，返回数据可用性）。"""
    try:
        from desktop.data_loader import load_draws  # type: ignore

        draws = load_draws()
        print(f"[worker] data check: {len(draws)} draws loaded")
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[worker] data check failed: {exc}")
        return False


def main() -> int:
    """运行 worker 主循环。"""
    interval = 5.0
    print("Atlas Worker v0.1.0 starting...")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            _refresh_data()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nWorker stopped gracefully.")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
