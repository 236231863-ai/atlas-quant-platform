"""Global Intelligence Dashboard - model network, nodes, agents, missions, exchanges."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class GlobalDashboardData:
    model_network: Dict[str, Any] = field(default_factory=dict)
    node_status: Dict[str, Any] = field(default_factory=dict)
    agent_activity: List[Dict[str, Any]] = field(default_factory=list)
    mission_progress: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_exchange: List[Dict[str, Any]] = field(default_factory=list)
    global_discoveries: List[Dict[str, Any]] = field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class GlobalDashboard:
    def __init__(self):
        self._data = GlobalDashboardData()
    def update_model_network(self, data: Dict[str, Any]):
        self._data.model_network = data
    def update_node_status(self, status: Dict[str, Any]):
        self._data.node_status = status
    def update_agent_activity(self, activity: List[Dict[str, Any]]):
        self._data.agent_activity = activity
    def update_mission_progress(self, progress: List[Dict[str, Any]]):
        self._data.mission_progress = progress
    def update_knowledge_exchange(self, exchange: List[Dict[str, Any]]):
        self._data.knowledge_exchange = exchange
    def update_global_discoveries(self, discoveries: List[Dict[str, Any]]):
        self._data.global_discoveries = discoveries
    def get_data(self) -> GlobalDashboardData: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"models": len(str(self._data.model_network)), "nodes": len(str(self._data.node_status)),
                "agents": len(self._data.agent_activity), "missions": len(self._data.mission_progress),
                "exchanges": len(self._data.knowledge_exchange)}
