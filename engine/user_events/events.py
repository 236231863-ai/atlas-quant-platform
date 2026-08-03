"""user_events - 用户行为事件追踪（v4.3 验收基础设施）。

验收标准升级：从「页面存在」到「用户行为发生」。
所有关键用户行为记录为事件：
  ticket_saved / reminder_shown / draw_countdown / claim_viewed /
  claim_confirmed / report_generated / app_opened

事件持久化到 ~/.atlas/events_v43.jsonl（支持 ATLAS_STORAGE_DIR）。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

EVENT_TYPES = {
    "app_opened", "ticket_saved", "reminder_shown", "draw_countdown",
    "claim_viewed", "claim_confirmed", "report_generated", "auto_claim_run",
}


@dataclass
class UserEvent:
    """一条用户行为事件。"""

    event_type: str
    payload: dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    user_id: str = "default"

    def to_dict(self) -> dict:
        return {"event_type": self.event_type, "payload": self.payload,
                "created_at": self.created_at, "user_id": self.user_id}


class EventTracker:
    """用户行为事件追踪器（jsonl 追加写）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "events_v43.jsonl")

    def record(self, event_type: str, payload: Optional[dict] = None) -> UserEvent:
        """记录一条事件（合法类型才记录）。"""
        if event_type not in EVENT_TYPES:
            return UserEvent(event_type="unknown", payload={"original": event_type})
        ev = UserEvent(event_type=event_type, payload=payload or {})
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return ev

    def all(self) -> List[UserEvent]:
        if not os.path.exists(self._path):
            return []
        out = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        out.append(UserEvent(**d))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def count(self, event_type: str) -> int:
        return sum(1 for e in self.all() if e.event_type == event_type)

    def count_since(self, event_type: str, since: str) -> int:
        """统计某时间点后的事件数（since 为 ISO 字符串）。"""
        return sum(1 for e in self.all()
                   if e.event_type == event_type and e.created_at >= since)

    def recent(self, event_type: str, limit: int = 20) -> List[UserEvent]:
        evs = [e for e in self.all() if e.event_type == event_type]
        return evs[-limit:]

    def summary(self) -> dict:
        """事件计数汇总（验收用）。"""
        evs = self.all()
        out = {"total": len(evs)}
        for t in EVENT_TYPES:
            out[t] = sum(1 for e in evs if e.event_type == t)
        return out

    def clear(self) -> None:
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass


def record_event(event_type: str, payload: Optional[dict] = None) -> UserEvent:
    """便捷函数：记录事件。"""
    return EventTracker().record(event_type, payload)
