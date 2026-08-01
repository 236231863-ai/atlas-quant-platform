"""Action Planning Engine - convert decisions into execution plans."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ActionPlanReport:
    plan_id:str
    goal:str
    steps:List[str]
    resources:Dict[str,float]
    timeline:str
    constraints:List[str]
    metrics:List[str]=field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class ActionPlanner:
    def __init__(self):
        self._plans: Dict[str, ActionPlanReport] = {}
    def create_plan(self, goal: str, steps: List[str]) -> ActionPlanReport:
        import uuid
        plan = ActionPlanReport(plan_id=str(uuid.uuid4()), goal=goal, steps=steps, resources={"compute":1.0}, timeline="7d", constraints=["budget","time"])
        self._plans[plan.plan_id] = plan; return plan
    def get_plan(self, pid: str) -> Optional[ActionPlanReport]: return self._plans.get(pid)
    def list_plans(self) -> List[ActionPlanReport]: return list(self._plans.values())
    def count(self) -> int: return len(self._plans)
