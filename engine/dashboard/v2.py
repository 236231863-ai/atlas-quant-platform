"""Research Dashboard Upgrade - agent status, team activity, debate history."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DashboardDataV2:
    agent_status: List[Dict[str, Any]] = field(default_factory=list)
    team_activity: List[Dict[str, Any]] = field(default_factory=list)
    debate_history: List[Dict[str, Any]] = field(default_factory=list)
    decision_timeline: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_evolution: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

class ResearchDashboardV2:
    def __init__(self): self._data = DashboardDataV2()
    def update_agent_status(self, agents: List[Dict[str, Any]]): self._data.agent_status = agents
    def update_team_activity(self, activities: List[Dict[str, Any]]): self._data.team_activity = activities
    def update_debate_history(self, debates: List[Dict[str, Any]]): self._data.debate_history = debates
    def update_decision_timeline(self, decisions: List[Dict[str, Any]]): self._data.decision_timeline = decisions
    def update_knowledge_evolution(self, evolution: Dict[str, Any]): self._data.knowledge_evolution = evolution
    def get_data(self) -> DashboardDataV2: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"active_agents": len(self._data.agent_status),
                "team_activities": len(self._data.team_activity),
                "debates_recorded": len(self._data.debate_history),
                "decisions_made": len(self._data.decision_timeline)}
