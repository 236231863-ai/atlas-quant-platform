"""Research Intelligence Router - route tasks to the right agent/model/node."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchExecutionPlan:
    agent: str; model: str; node: str; strategy: str; reason: str
    def to_dict(self):
        return asdict(self)

class IntelligenceRouter:
    def route(self, goal_type: str, complexity: float, risk_level: float) -> ResearchExecutionPlan:
        if risk_level > 0.7: agent = "risk_agent"; model = "conservative"
        elif complexity > 0.7: agent = "strategy_architect"; model = "analytical"
        else: agent = "discovery_agent"; model = "exploratory"
        node = "local_node"; strategy = "standard"
        return ResearchExecutionPlan(agent=agent, model=model, node=node, strategy=strategy,
            reason=f"Goal type: {goal_type}, complexity: {complexity}, risk: {risk_level}")
    def select_model(self, task_type: str, models: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        candidates = [m for m in models if task_type in m.get("capabilities", [])]
        if not candidates: return None
        return max(candidates, key=lambda m: m.get("quality_score", 0))
    def select_agent(self, task_type: str, agents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        candidates = [a for a in agents if task_type in a.get("skills", [])]
        if not candidates: return None
        return max(candidates, key=lambda a: a.get("efficiency", 1))
