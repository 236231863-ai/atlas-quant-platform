"""Action API - expose action planning and feedback capabilities."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.action import ActionPlanner, ActionPlanReport

class ActionAPIService:
    def __init__(self):
        self._planner = ActionPlanner()
    def create_plan(self, goal: str, steps: List[str]) -> ActionPlanReport: return self._planner.create_plan(goal, steps)
    def get_plans(self) -> List[ActionPlanReport]: return self._planner.list_plans()
    def get_status(self, pid: str) -> Optional[ActionPlanReport]: return self._planner.get_plan(pid)
    def count(self) -> int: return self._planner.count()
