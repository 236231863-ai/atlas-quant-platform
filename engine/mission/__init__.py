"""Long Horizon Research Mission System - months/years research tasks."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchMission:
    mission_id: str; objective: str; duration_days: int; milestones: List[str]
    resources: Dict[str, float]; status: str = "active"; progress: float = 0.0
    def to_dict(self):
        return asdict(self)

class ResearchMissionManager:
    def __init__(self):
        self._missions: Dict[str, ResearchMission] = {}
    def create_mission(self, mission: ResearchMission):
        self._missions[mission.mission_id] = mission
        return mission
    def get_mission(self, mid: str) -> Optional[ResearchMission]: return self._missions.get(mid)
    def update_progress(self, mid: str, progress: float) -> bool:
        m = self._missions.get(mid)
        if not m: return False
        m.progress = min(1.0, progress); return True
    def evaluate_milestone(self, mid: str, milestone_idx: int) -> bool:
        m = self._missions.get(mid)
        if not m or milestone_idx >= len(m.milestones): return False
        m.progress = (milestone_idx + 1) / len(m.milestones); return True
    def complete_mission(self, mid: str) -> bool:
        m = self._missions.get(mid)
        if not m: return False
        m.status = "completed"; m.progress = 1.0; return True
    def list_missions(self) -> List[ResearchMission]: return list(self._missions.values())
    def count(self) -> int: return len(self._missions)
