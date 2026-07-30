"""User Digital Profile System - comprehensive user understanding."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

UserLevel = Enum("UserLevel", ["BEGINNER","EXPLORER","ADVANCED","RESEARCHER","PROFESSIONAL","SCIENTIST"])

@dataclass
class UserDigitalProfile: user_id:str; level:UserLevel=UserLevel.BEGINNER; skill_level:float=0.0; research_interests:List[str]=field(default_factory=list); favorite_strategy:str=""; risk_preference:float=0.5; usage_pattern:str="balanced"; learning_progress:float=0.0; def to_dict(self):return asdict(self)

class ProfileEvolutionEngine:
    def __init__(self): self._profiles: Dict[str, UserDigitalProfile] = {}
    def update_profile(self, uid: str, events: List[Dict]) -> UserDigitalProfile:
        profile = self._profiles.get(uid, UserDigitalProfile(user_id=uid))
        analysis_count = sum(1 for e in events if e.get("event_type","").startswith("analysis"))
        if analysis_count > 200: profile.level = UserLevel.SCIENTIST; profile.skill_level = 1.0
        elif analysis_count > 100: profile.level = UserLevel.PROFESSIONAL; profile.skill_level = 0.8
        elif analysis_count > 50: profile.level = UserLevel.RESEARCHER; profile.skill_level = 0.6
        elif analysis_count > 20: profile.level = UserLevel.ADVANCED; profile.skill_level = 0.4
        elif analysis_count > 5: profile.level = UserLevel.EXPLORER; profile.skill_level = 0.2
        self._profiles[uid] = profile; return profile
    def predict_next_stage(self, uid: str) -> str:
        p = self._profiles.get(uid)
        if not p: return "Start with basic analysis"
        if p.level == UserLevel.BEGINNER: return "Try 5 more analyses to reach Explorer"
        if p.level == UserLevel.EXPLORER: return "Complete 20 analyses to reach Advanced"
        return "Advanced features available"
    def get_profile(self, uid: str) -> Optional[UserDigitalProfile]: return self._profiles.get(uid)
    def count(self) -> int: return len(self._profiles)
