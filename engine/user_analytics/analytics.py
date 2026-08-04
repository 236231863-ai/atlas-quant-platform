"""user_analytics.analytics - 用户事件分析（v4.6 P1）。

标准化事件格式：{event_name, timestamp, user_id, source, metadata}
8 类核心事件：app_opened / ticket_saved / ticket_checked / reminder_clicked /
             claim_completed / report_viewed / budget_viewed / export_clicked

存储：~/.atlas/analytics_v46.jsonl（支持 ATLAS_STORAGE_DIR 隔离）
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

EVENT_NAMES = (
    "app_opened", "ticket_saved", "ticket_checked", "reminder_clicked",
    "claim_completed", "report_viewed", "budget_viewed", "export_clicked",
    # v4.6 P6：商业化
    "premium_view", "premium_click",
)


@dataclass
class AnalyticsEvent:
    """一条标准化用户行为事件。"""

    event_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    user_id: str = "default"
    source: str = "desktop"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"event_name": self.event_name, "timestamp": self.timestamp,
                "user_id": self.user_id, "source": self.source,
                "metadata": dict(self.metadata)}


class AnalyticsTracker:
    """用户事件追踪器（标准化 8 事件）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "analytics_v46.jsonl")

    def record(self, event_name: str, source: str = "desktop",
               metadata: Optional[dict] = None,
               user_id: str = "default") -> Optional[AnalyticsEvent]:
        """记录一条事件（非法事件名返回 None）。"""
        if event_name not in EVENT_NAMES:
            return None
        ev = AnalyticsEvent(event_name=event_name, user_id=user_id,
                            source=source, metadata=metadata or {})
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return ev

    def all(self) -> List[AnalyticsEvent]:
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
                        out.append(AnalyticsEvent(**d))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def count(self, event_name: str) -> int:
        return sum(1 for e in self.all() if e.event_name == event_name)

    def recent(self, event_name: str, limit: int = 20) -> List[AnalyticsEvent]:
        evs = [e for e in self.all() if e.event_name == event_name]
        return evs[-limit:]

    def summary(self) -> dict:
        evs = self.all()
        out = {"total": len(evs)}
        for name in EVENT_NAMES:
            out[name] = sum(1 for e in evs if e.event_name == name)
        return out

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass


def track(event_name: str, source: str = "desktop",
          metadata: Optional[dict] = None) -> Optional[AnalyticsEvent]:
    """便捷函数。"""
    return AnalyticsTracker().record(event_name, source=source, metadata=metadata)
