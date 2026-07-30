"""Dashboard Ecosystem Layer - agent ranking, evolution, competitions, resources."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class EcosystemDashboardData:
    agent_ranking: List[Dict[str, Any]] = field(default_factory=list)
    evolution_tree: List[Dict[str, Any]] = field(default_factory=list)
    competition_history: List[Dict[str, Any]] = field(default_factory=list)
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    civilization_timeline: List[Dict[str, Any]] = field(default_factory=list)
    def to_dict(self): return asdict(self)

class DashboardEcosystemLayer:
    def __init__(self): self._data = EcosystemDashboardData()
    def update_agent_ranking(self, ranking: List[Dict[str, Any]]): self._data.agent_ranking = ranking
    def update_evolution_tree(self, tree: List[Dict[str, Any]]): self._data.evolution_tree = tree
    def update_competition_history(self, history: List[Dict[str, Any]]): self._data.competition_history = history
    def update_resource_allocation(self, allocation: Dict[str, Any]): self._data.resource_allocation = allocation
    def update_civilization_timeline(self, timeline: List[Dict[str, Any]]): self._data.civilization_timeline = timeline
    def get_data(self) -> EcosystemDashboardData: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"agents_ranked": len(self._data.agent_ranking),
                "evolution_nodes": len(self._data.evolution_tree),
                "competitions": len(self._data.competition_history),
                "eras_tracked": len(self._data.civilization_timeline)}
