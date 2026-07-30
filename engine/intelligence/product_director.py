"""AI Product Manager - analyze users, discover problems, optimize product."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class FeatureRecommendation: feature:str; priority:int=5; impact:float=0.5; cost:float=0.5; risk:float=0.3; expected_value:float=0.0; def to_dict(self):return asdict(self)

class AIProductDirector:
    def __init__(self): self._recommendations: List[FeatureRecommendation] = []
    def analyze_user_needs(self, profiles: List[Dict]) -> List[str]:
        low_level = sum(1 for p in profiles if p.get("level","").value=="BEGINNER")
        return ["Simplify onboarding"] if low_level > len(profiles)/2 else ["Advanced features ready"]
    def generate_roadmap(self, features: List[FeatureRecommendation]) -> List[FeatureRecommendation]:
        for f in features: f.expected_value = round(f.impact * 0.5 + (1/f.cost) * 0.3 + (1-f.risk) * 0.2, 4)
        return sorted(features, key=lambda f: f.expected_value, reverse=True)
    def count(self) -> int: return len(self._recommendations)
