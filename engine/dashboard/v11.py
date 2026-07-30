"""Autonomous Intelligence Dashboard - action timeline, execution status, feedback, learning."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AutonomousDashboardData: action_timeline:List[Dict]=field(default_factory=list); execution_status:Dict[str,Any]=field(default_factory=dict); feedback_history:List[Dict]=field(default_factory=list); learning_curve:List[float]=field(default_factory=list); improvement_score:float=0.0; def to_dict(self):return asdict(self)

class AutonomousDashboard:
    def __init__(self): self._data = AutonomousDashboardData()
    def update_timeline(self, t): self._data.action_timeline = t
    def update_execution(self, s): self._data.execution_status = s
    def update_feedback(self, f): self._data.feedback_history = f
    def update_learning(self, l): self._data.learning_curve = l
    def get_data(self) -> AutonomousDashboardData: return self._data
    def summary(self): return {"actions": len(self._data.action_timeline), "feedback": len(self._data.feedback_history), "improvement": self._data.improvement_score}
