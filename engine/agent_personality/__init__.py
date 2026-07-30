"""Research Personality System - unique agent behavior profiles."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class PersonalityProfile:
    agent_id: str; risk_preference: float = 0.5; exploration_level: float = 0.5
    analysis_depth: float = 0.5; decision_style: str = "balanced"; confidence_level: float = 0.5
    def to_dict(self): return asdict(self)

class PersonalityManager:
    def __init__(self): self._profiles: Dict[str, PersonalityProfile] = {}
    def create_profile(self, agent_id: str, **kwargs) -> PersonalityProfile:
        profile = PersonalityProfile(agent_id=agent_id, **kwargs)
        self._profiles[agent_id] = profile; return profile
    def get_profile(self, agent_id: str) -> Optional[PersonalityProfile]: return self._profiles.get(agent_id)
    def evaluate_behavior(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        profile = self._profiles.get(agent_id)
        if not profile: return {"suitability": 0.5}
        suit = profile.analysis_depth * 0.4 + profile.confidence_level * 0.3 + profile.risk_preference * 0.3
        return {"agent_id": agent_id, "suitability": round(suit, 2), "style": profile.decision_style}
    def adapt_personality(self, agent_id: str, adjustments: Dict[str, float]) -> bool:
        profile = self._profiles.get(agent_id)
        if not profile: return False
        for key, val in adjustments.items():
            if hasattr(profile, key): setattr(profile, key, max(0.0, min(1.0, getattr(profile, key) + val)))
        return True
    def list_profiles(self) -> List[PersonalityProfile]: return list(self._profiles.values())
    def count(self) -> int: return len(self._profiles)
