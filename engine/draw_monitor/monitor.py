"""draw_monitor.monitor - 自动开奖监控（v4.5 P2）。

后台检测开奖日（大乐透一/三/六、双色球二/四/日）：
  开奖时间到 → 检查数据 → 更新开奖 → 触发 draw_updated 事件

复用 v4.4 live_draw.service（should_check/check_once）+ LotterySchedule。
"""
from __future__ import annotations

import threading
from datetime import date, datetime, timedelta
from typing import Callable, List, Optional

from engine.live_draw.events import DrawEvent, DrawEventBus
from engine.live_draw.service import LiveDrawService
from engine.ticket_system.schedule import LotterySchedule

LOTTERIES = [("dlt", "大乐透"), ("ssq", "双色球")]
CHECK_INTERVAL_SECONDS = 30 * 60


class DrawMonitor:
    """自动开奖监控器。"""

    def __init__(self, service: Optional[LiveDrawService] = None,
                 event_bus=None):
        self.service = service or LiveDrawService()
        self.event_bus = event_bus or DrawEventBus

    # ---------- 开奖日程 ----------
    @staticmethod
    def is_draw_day(lottery: str, day: Optional[str] = None) -> bool:
        day = day or date.today().isoformat()
        return LotterySchedule.is_draw_day(lottery, day)

    @staticmethod
    def next_draw_time(lottery: str, from_date: Optional[str] = None) -> str:
        """下一开奖日。"""
        from_date = from_date or date.today().isoformat()
        return LotterySchedule.next_draw_date(lottery, from_date) or ""

    def upcoming_draws(self, n: int = 3) -> List[dict]:
        """最近 n 个开奖日程（双彩种混合排序）。"""
        out = []
        for lottery, name in LOTTERIES:
            d = self.next_draw_time(lottery)
            if d:
                out.append({"lottery": lottery, "lottery_name": name, "date": d})
        out.sort(key=lambda x: x["date"])
        return out[:n]

    # ---------- 监控一次 ----------
    def monitor_once(self, now: Optional[datetime] = None) -> List[DrawEvent]:
        """监控一次：对每个彩种按需检查并发布事件。"""
        now = now or datetime.now()
        events = []
        for lottery, _ in LOTTERIES:
            if self.service.should_check(lottery, now=now):
                ev = self.service.check_once(lottery)
                events.append(ev)
            else:
                # 无需检查：发布 sync_skipped 保持监控透明度
                events.append(DrawEvent(event_type="sync_skipped", lottery=lottery,
                                        reason="not_due"))
        return events

    # ---------- 后台循环 ----------
    def run_loop(self, interval_seconds: int = CHECK_INTERVAL_SECONDS,
                 stop_event: Optional[threading.Event] = None,
                 callback: Optional[Callable] = None) -> None:
        """后台监控循环。"""
        stop = stop_event or threading.Event()
        while not stop.is_set():
            events = self.monitor_once()
            if callback:
                for ev in events:
                    try:
                        callback(ev)
                    except Exception:
                        continue
            stop.wait(interval_seconds)

    def run_background(self, interval_seconds: int = CHECK_INTERVAL_SECONDS) -> threading.Event:
        """启动后台监控线程。"""
        stop = threading.Event()
        t = threading.Thread(target=self.run_loop,
                             kwargs={"interval_seconds": interval_seconds,
                                     "stop_event": stop},
                             daemon=True)
        t.start()
        return stop

    # ---------- 下一开奖倒计时 ----------
    def countdown_text(self, lottery: str = "dlt") -> str:
        """「距离下一开奖」文案。"""
        nxt = self.next_draw_time(lottery)
        if not nxt:
            return "暂无开奖日程"
        try:
            d = datetime.strptime(nxt, "%Y-%m-%d").date()
            days = (d - date.today()).days
            name = "大乐透" if lottery == "dlt" else "双色球"
            if days <= 0:
                return f"{name} 今日开奖"
            return f"{name} 距开奖 {days} 天（{nxt}）"
        except ValueError:
            return f"{name} {nxt}"


def monitor_now() -> List[DrawEvent]:
    """便捷函数：立即监控一次。"""
    return DrawMonitor().monitor_once()
