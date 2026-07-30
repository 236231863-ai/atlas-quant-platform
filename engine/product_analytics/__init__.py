"""Product Analytics System - understand user interactions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class UserEvent:
    event_id: str; user_id: str; event_type: str; timestamp: str; metadata: Dict[str, Any]=field(default_factory=dict)
    def to_dict(self): return asdict(self)

EVENT_TYPES = ["USER_LOGIN","ANALYSIS_START","ANALYSIS_COMPLETE","REPORT_VIEW","REPORT_SAVE","STRATEGY_FAVORITE","BACKTEST_RUN","COMMUNITY_SHARE"]

class EventTracker:
    def __init__(self): self._events: List[UserEvent] = []
    def track(self, event: UserEvent): self._events.append(event); return event
    def get_events(self, event_type: Optional[str]=None) -> List[UserEvent]:
        if event_type: return [e for e in self._events if e.event_type==event_type]
        return self._events
    def count(self) -> int: return len(self._events)

class ProductMetricsEngine:
    def __init__(self): self._tracker = EventTracker()
    def compute_dau(self, events: List[UserEvent]) -> int: return len(set(e.user_id for e in events))
    def compute_feature_usage(self, events: List[UserEvent]) -> Dict[str, int]:
        usage = {}
        for e in events:
            usage[e.event_type] = usage.get(e.event_type,0)+1
        return usage
    def get_tracker(self): return self._tracker
