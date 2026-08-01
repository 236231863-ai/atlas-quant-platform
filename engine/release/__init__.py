"""Release Intelligence Engine - smart continuous delivery and canary releases."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ReleasePlan:
    version:str
    canary_percent:float=0.1
    risk_score:float=0.0
    suggested_action:str=""
    rollback_plan:str=""
    def to_dict(self):
        return asdict(self)

class ReleaseIntelligenceEngine:
    def __init__(self):
        self._releases: List[ReleasePlan] = []
    def plan_release(self, version: str, changes: int) -> ReleasePlan:
        risk = min(1.0, changes * 0.01)
        p = ReleasePlan(version=version, canary_percent=0.1, risk_score=round(risk,4), suggested_action="canary_deploy" if risk<0.3 else "gradual_rollout", rollback_plan="auto_rollback_previous_version")
        self._releases.append(p); return p
    def get_history(self) -> List[ReleasePlan]: return self._releases
    def count(self) -> int: return len(self._releases)
