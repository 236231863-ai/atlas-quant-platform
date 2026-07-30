"""AI Researcher Career System - manage scientist evolution."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

class CareerLevel(str, Enum):
    INTERN = "intern_scientist"; RESEARCH = "research_scientist"
    SENIOR = "senior_scientist"; PRINCIPAL = "principal_scientist"; DIRECTOR = "research_director"

LEVELS = [CareerLevel.INTERN, CareerLevel.RESEARCH, CareerLevel.SENIOR, CareerLevel.PRINCIPAL, CareerLevel.DIRECTOR]

@dataclass
class ScientistProfile:
    scientist_id: str; name: str; level: CareerLevel = CareerLevel.INTERN
    research_quality: float = 0.3; innovation_score: float = 0.3
    publication_score: float = 0.0; teamwork_score: float = 0.3
    def to_dict(self): return asdict(self)

class ResearchCareerManager:
    def __init__(self): self._scientists: Dict[str, ScientistProfile] = {}
    def register(self, profile: ScientistProfile): self._scientists[profile.scientist_id] = profile; return profile
    def evaluate(self, sid: str) -> Optional[float]:
        s = self._scientists.get(sid)
        if not s: return None
        return round((s.research_quality + s.innovation_score + s.publication_score + s.teamwork_score) / 4, 2)
    def promote(self, sid: str) -> bool:
        s = self._scientists.get(sid)
        if not s: return False
        overall = self.evaluate(sid) or 0
        idx = LEVELS.index(s.level) if s.level in LEVELS else -1
        if idx >= len(LEVELS) - 1: return False
        threshold = 0.3 + idx * 0.15
        if overall >= threshold:
            s.level = LEVELS[idx + 1]; return True
        return False
    def list_scientists(self) -> List[ScientistProfile]: return list(self._scientists.values())
    def count(self) -> int: return len(self._scientists)
