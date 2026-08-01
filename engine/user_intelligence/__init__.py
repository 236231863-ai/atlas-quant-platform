"""User Intelligence Engine - understand users through behavior analysis."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

class UserLevel(str, Enum):
    BEGINNER="beginner"
    EXPLORER="explorer"
    ADVANCED="advanced"
    RESEARCHER="researcher"
    PROFESSIONAL="professional"
    ENTERPRISE="enterprise"

@dataclass
class UserIntelligenceProfile:
    user_id:str
    level:UserLevel=UserLevel.BEGINNER
    skill_score:float=0.0
    interests:List[str]=field(default_factory=list)
    preferred_strategies:List[str]=field(default_factory=list)
    analysis_count:int=0
    recommendation:str="start with basic analysis"
    def to_dict(self):
        return asdict(self)

class UserIntelligenceEngine:
    def __init__(self):
        self._profiles: Dict[str, UserIntelligenceProfile] = {}
    def analyze_user(self, uid: str, events: List[Dict[str, Any]]) -> UserIntelligenceProfile:
        analysis_count = sum(1 for e in events if e.get("type")=="analysis")
        profile = UserIntelligenceProfile(user_id=uid)
        profile.analysis_count = analysis_count
        if analysis_count > 100: profile.level = UserLevel.PROFESSIONAL; profile.skill_score = 0.9; profile.recommendation = "Enable advanced models and experiment tools"
        elif analysis_count > 50: profile.level = UserLevel.ADVANCED; profile.skill_score = 0.7; profile.recommendation = "Try strategy comparison and backtesting"
        elif analysis_count > 10: profile.level = UserLevel.EXPLORER; profile.skill_score = 0.4; profile.recommendation = "Explore different strategies"
        self._profiles[uid] = profile; return profile
    def get_profile(self, uid: str) -> Optional[UserIntelligenceProfile]: return self._profiles.get(uid)
    def calculate_skill_level(self, uid: str) -> float:
        p = self._profiles.get(uid); return p.skill_score if p else 0.0
    def count(self) -> int: return len(self._profiles)
