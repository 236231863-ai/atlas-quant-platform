"""live_draw.service - Live Draw Engine（v4.4 P1）。

后台开奖同步服务：
  - 自动检测最新期号（对比本地缓存 vs 官方 API）
  - 新期发现 → 发布 new_issue 事件
  - 更新成功 → 发布 draw_updated 事件
  - 数据校验 + 防旧覆盖（复用 updater 的 no_new / _valid_remote）
  - 更新失败 → 发布 update_failed 事件（静默降级）

开奖节奏：大乐透一/三/六、双色球二/四/日（复用 LotterySchedule）。
"""
from __future__ import annotations

import threading
import time
from datetime import date, datetime, timedelta
from typing import Callable, List, Optional

from engine.live_draw.events import DrawEvent, DrawEventBus
from engine.ticket_system.schedule import LotterySchedule

LOTTERIES = [("dlt", "大乐透"), ("ssq", "双色球")]
CHECK_INTERVAL_SECONDS = 30 * 60          # 后台循环默认 30 分钟
STALE_HOURS = 12                          # 超过 12h 视为需检查


class LiveDrawService:
    """开奖实时同步服务。"""

    def __init__(self, storage_dir: Optional[str] = None, event_bus=None):
        self.storage_dir = storage_dir
        self.event_bus = event_bus or DrawEventBus

    # ---------- 内部工具 ----------
    def _local_latest_issue(self, lottery: str) -> str:
        """读取本地缓存最新期号。"""
        from engine.data_center_v2.updater import IncrementalUpdater
        up = IncrementalUpdater(lottery, storage_dir=self.storage_dir)
        rows = up.load_local()
        if not rows:
            rows = up._load_builtin()
        return rows[-1]["issue"] if rows else ""

    def _emit(self, event_type: str, lottery: str, **kw) -> DrawEvent:
        ev = DrawEvent(event_type=event_type, lottery=lottery, **kw)
        self.event_bus.publish(ev)
        return ev

    # ---------- 核心：检查一次 ----------
    def check_once(self, lottery: str = "dlt", force: bool = False) -> DrawEvent:
        """检查一次：拉取官方最新 → 有新增则更新并发布事件。

        返回 DrawEvent：
          - draw_updated / new_issue（成功）
          - sync_skipped（无新期）
          - update_failed（失败）
        """
        from engine.data_center_v2.updater import IncrementalUpdater

        before = self._local_latest_issue(lottery)
        up = IncrementalUpdater(lottery, storage_dir=self.storage_dir)
        result = up.update(force=force)
        after = self._local_latest_issue(lottery)

        # 未更新：区分「无新期/限频=skipped」vs「失败=failed」
        if not result.get("updated"):
            reason = result.get("reason", "")
            if reason in ("no_new", "within_age"):
                return self._emit("sync_skipped", lottery,
                                  issue=before, reason=reason)
            return self._emit("update_failed", lottery,
                              error=result.get("error", ""),
                              reason=reason, issue=before)

        # 成功
        issue = result.get("issue", "") or after
        # 新期发现：更新后最新期号前进
        if after and before and after != before:
            self._emit("new_issue", lottery, issue=after,
                       draw_date=self._draw_date_of(lottery, after),
                       added=result.get("added", 0), total=result.get("total", 0))
        return self._emit("draw_updated", lottery, issue=issue,
                          draw_date=self._draw_date_of(lottery, issue),
                          added=result.get("added", 0),
                          total=result.get("total", 0))

    def _draw_date_of(self, lottery: str, issue: str) -> str:
        """查找某期号的开奖日期（从本地缓存）。"""
        from engine.data_center_v2.updater import IncrementalUpdater
        up = IncrementalUpdater(lottery, storage_dir=self.storage_dir)
        for r in up.load_local():
            if r["issue"] == issue:
                return r["date"]
        return ""

    # ---------- 全彩种同步 ----------
    def sync_all(self, force: bool = False) -> List[DrawEvent]:
        """同步所有彩种。"""
        events = []
        for lottery, _ in LOTTERIES:
            events.append(self.check_once(lottery, force=force))
        return events

    # ---------- 智能检查时机 ----------
    def should_check(self, lottery: str, now: Optional[datetime] = None) -> bool:
        """是否该检查：开奖日当天 或 数据已过期（>12h）。"""
        now = now or datetime.now()
        today = now.date().isoformat()
        if LotterySchedule.is_draw_day(lottery, today):
            return True
        # 非开奖日：看更新时间是否过期
        from engine.data_center_v2.updater import IncrementalUpdater
        up = IncrementalUpdater(lottery, storage_dir=self.storage_dir)
        last = up._last_update()
        if not last:
            return True
        try:
            dt = datetime.fromisoformat(last)
            return (now - dt) > timedelta(hours=STALE_HOURS)
        except ValueError:
            return True

    # ---------- 后台循环 ----------
    def auto_sync_loop(self, interval_seconds: int = CHECK_INTERVAL_SECONDS,
                       stop_event: Optional[threading.Event] = None,
                       callback: Optional[Callable] = None) -> None:
        """后台自动同步循环（供线程/服务调用）。

        每次循环：对每个彩种按 should_check 决定是否检查。
        stop_event 置位时优雅退出。
        """
        stop = stop_event or threading.Event()
        while not stop.is_set():
            for lottery, _ in LOTTERIES:
                if self.should_check(lottery):
                    ev = self.check_once(lottery)
                    if callback:
                        try:
                            callback(ev)
                        except Exception:
                            pass
            stop.wait(interval_seconds)

    def run_loop_background(self, interval_seconds: int = CHECK_INTERVAL_SECONDS) -> threading.Event:
        """启动后台循环线程，返回 stop_event。"""
        stop = threading.Event()
        t = threading.Thread(target=self.auto_sync_loop,
                             kwargs={"interval_seconds": interval_seconds,
                                     "stop_event": stop},
                             daemon=True)
        t.start()
        return stop


def sync_now(force: bool = False) -> List[DrawEvent]:
    """便捷函数：立即同步所有彩种。"""
    return LiveDrawService().sync_all(force=force)
