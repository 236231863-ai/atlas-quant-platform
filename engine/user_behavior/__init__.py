"""User Behavior Intelligence Layer - track and analyze real user behavior."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

class UserBehaviorEvent:
    def __init__(self, uid: str, event_type: str, feature: str = "", duration: float = 0.0, result: str = "", feedback: str = ""):
        import uuid, datetime; self.event_id = str(uuid.uuid4()); self.user_id = uid; self.event_type = event_type
        self.timestamp = datetime.datetime.now().isoformat(); self.feature = feature; self.duration = duration; self.result = result; self.feedback = feedback
    def to_dict(self):
        return {"event_id": self.event_id, "user_id": self.user_id, "event_type": self.event_type,
        "feature": self.feature, "duration": self.duration, "result": self.result, "feedback": self.feedback}

EVENT_TYPES = ["login","analysis_start","analysis_complete","strategy_generate","report_view","strategy_save","strategy_modify","strategy_share","subscription_change"]

class BehaviorAnalyzer:
    def __init__(self):
        self._events: List[UserBehaviorEvent] = []
    def record(self, e: UserBehaviorEvent):
        self._events.append(e)
        return e
    def interest_analysis(self, uid: str) -> List[str]:
        user_events = [e for e in self._events if e.user_id == uid]
        features = {}
        for e in user_events: features[e.feature] = features.get(e.feature, 0) + 1
        return sorted(features, key=features.get, reverse=True)[:3]
    def churn_risk(self, uid: str) -> float:
        recent = [e for e in self._events if e.user_id == uid][-20:]
        if len(recent) < 5: return 0.0
        recent_analysis = sum(1 for e in recent if "analysis" in e.event_type)
        return max(0.0, 1.0 - recent_analysis / max(len(recent), 1))
    def count(self) -> int: return len(self._events)
