"""User Intelligence Profile - understand user behavior and preferences."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

class UserType(str, Enum): BEGINNER="beginner"; EXPLORER="explorer"; ADVANCED="advanced"; RESEARCHER="researcher"

@dataclass
class UserProfile:
    user_id: str; user_type: UserType=UserType.BEGINNER; experience_level: float=0.1
    favorite_features: List[str]=field(default_factory=list); analysis_style: str="balanced"
    risk_preference: float=0.5; preferred_report_type: str="simple"
    def to_dict(self): return asdict(self)

class UserProfileEngine:
    def __init__(self): self._profiles: Dict[str, UserProfile] = {}
    def analyze_behavior(self, uid: str, events: List[Dict[str, Any]]) -> UserProfile:
        profile = self._profiles.get(uid, UserProfile(user_id=uid))
        report_views = sum(1 for e in events if e.get("event_type")=="REPORT_VIEW")
        backtest_runs = sum(1 for e in events if e.get("event_type")=="BACKTEST_RUN")
        if report_views > 20 and backtest_runs > 10: profile.user_type = UserType.RESEARCHER; profile.experience_level=0.9
        elif report_views > 10: profile.user_type = UserType.ADVANCED; profile.experience_level=0.6
        elif backtest_runs > 0: profile.user_type = UserType.EXPLORER; profile.experience_level=0.3
        self._profiles[uid] = profile; return profile
    def get_profile(self, uid: str) -> Optional[UserProfile]: return self._profiles.get(uid)
    def recommend_features(self, uid: str) -> List[str]:
        p = self._profiles.get(uid)
        if not p: return ["basic_analysis"]
        if p.user_type == UserType.BEGINNER: return ["basic_analysis","simple_report"]
        if p.user_type == UserType.RESEARCHER: return ["advanced_analysis","backtesting","experiments"]
        return ["basic_analysis","strategy_comparison","report"]
    def count(self) -> int: return len(self._profiles)
