"""Research Resource Allocation - optimize research resources."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AllocationPlan:
    experiments_allowed: int; compute_budget: float; priority_levels: Dict[str, int]
    agent_workload: Dict[str, int]
    def to_dict(self):
        return asdict(self)

class ResearchResourceAllocator:
    def __init__(self):
        self._agents: Dict[str, float] = {}
    def register_agent(self, agent_id: str, efficiency: float = 1.0):
        self._agents[agent_id] = efficiency
    def allocate_experiments(self, total_budget: int, agent_scores: Dict[str, float]) -> AllocationPlan:
        if not agent_scores: return AllocationPlan(0,0,{},{})
        total_score = sum(agent_scores.values()) or 1
        workload = {}
        for agent, score in agent_scores.items():
            workload[agent] = max(1, int(total_budget * score / total_score))
        return AllocationPlan(experiments_allowed=total_budget, compute_budget=float(total_budget),
            priority_levels={a: 5 for a in agent_scores}, agent_workload=workload)
    def get_priority(self, urgency: float, research_value: float) -> int:
        return min(10, max(1, int((urgency * 0.6 + research_value * 0.4) * 10)))
    def count_agents(self) -> int: return len(self._agents)
