"""live_draw.events - 开奖同步事件（v4.4 P1）。

事件总线 + 事件类型：
  - draw_updated   （数据成功更新到新期）
  - new_issue      （发现新期号）
  - update_failed  （同步失败，含原因）
  - sync_skipped   （无新期，数据已最新）

DrawUpdated Event 是 P4 自动兑奖联动、P5 UI 刷新的触发源。
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List

EVENT_TYPES = ("draw_updated", "new_issue", "update_failed", "sync_skipped")

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class DrawEvent:
    """一条开奖同步事件。"""

    event_type: str
    lottery: str
    issue: str = ""
    draw_date: str = ""
    added: int = 0
    total: int = 0
    error: str = ""
    reason: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def lottery_name(self) -> str:
        return LOTTERY_NAMES.get(self.lottery, self.lottery)

    def to_dict(self) -> dict:
        return {"event_type": self.event_type, "lottery": self.lottery,
                "lottery_name": self.lottery_name, "issue": self.issue,
                "draw_date": self.draw_date, "added": self.added,
                "total": self.total, "error": self.error,
                "reason": self.reason, "created_at": self.created_at}


class DrawEventBus:
    """内存事件总线：订阅 / 发布。"""

    _subscribers: Dict[str, List[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable) -> None:
        """订阅某类事件。"""
        if event_type not in EVENT_TYPES:
            event_type = "draw_updated"
        cls._subscribers[event_type].append(callback)

    @classmethod
    def publish(cls, event: DrawEvent) -> None:
        """发布事件给所有订阅者。"""
        for cb in list(cls._subscribers.get(event.event_type, [])):
            try:
                cb(event)
            except Exception:
                continue

    @classmethod
    def reset(cls) -> None:
        """清空订阅（测试隔离用）。"""
        cls._subscribers.clear()

    @classmethod
    def subscriber_count(cls, event_type: str) -> int:
        return len(cls._subscribers.get(event_type, []))


def on_draw_updated(callback: Callable) -> Callable:
    """装饰器：订阅 draw_updated 事件。"""
    DrawEventBus.subscribe("draw_updated", callback)
    return callback


def on_new_issue(callback: Callable) -> Callable:
    """装饰器：订阅 new_issue 事件。"""
    DrawEventBus.subscribe("new_issue", callback)
    return callback
