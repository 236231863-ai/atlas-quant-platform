"""Autonomous Goal Discovery Engine - discover research opportunities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchGoal:
    goal_id: str; title: str; reason: str; priority: float = 0.5
    expected_value: float = 0.5; risk: float = 0.3; source: str = "analysis"
    def to_dict(self):
        return asdict(self)

class ResearchGoalGenerator:
    def __init__(self):
        self._goals: Dict[str, ResearchGoal] = {}
    def generate_goal(self, goal: ResearchGoal) -> ResearchGoal:
        self._goals[goal.goal_id] = goal; return goal
    def get_goal(self, gid: str) -> Optional[ResearchGoal]: return self._goals.get(gid)
    def rank_goals(self) -> List[ResearchGoal]:
        return sorted(self._goals.values(), key=lambda g: g.priority * g.expected_value / max(g.risk, 0.01), reverse=True)
    def merge_goals(self, gid1: str, gid2: str) -> Optional[ResearchGoal]:
        g1, g2 = self._goals.get(gid1), self._goals.get(gid2)
        if not g1 or not g2: return None
        merged = ResearchGoal(goal_id=f"merged_{gid1}_{gid2}", title=f"{g1.title} + {g2.title}",
            reason=f"{g1.reason}; {g2.reason}", priority=(g1.priority+g2.priority)/2,
            expected_value=(g1.expected_value+g2.expected_value)/2, risk=max(g1.risk,g2.risk), source="merge")
        self._goals[merged.goal_id] = merged; return merged
    def evaluate_goal(self, gid: str) -> Dict[str, float]:
        g = self._goals.get(gid)
        if not g: return {"score": 0}
        score = g.priority * g.expected_value / max(g.risk, 0.01)
        return {"priority_score": round(g.priority, 2), "value_score": round(g.expected_value, 2),
                "risk_score": round(g.risk, 2), "overall_score": round(score, 2)}
    def list_goals(self) -> List[ResearchGoal]: return list(self._goals.values())
    def count(self) -> int: return len(self._goals)
