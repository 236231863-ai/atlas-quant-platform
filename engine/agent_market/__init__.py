"""AI Agent Marketplace - custom AI research agents."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AgentAsset:
    agent_id:str
    creator:str
    capabilities:List[str]
    version:str="1.0"
    permissions:List[str]=field(default_factory=list)
    rating:float=0.0
    status:str="draft"
    def to_dict(self):
        return asdict(self)

class AgentMarketplace:
    def __init__(self):
        self._agents: Dict[str, AgentAsset] = {}
    def register(self, agent: AgentAsset):
        self._agents[agent.agent_id] = agent
        return agent
    def publish(self, agent_id: str) -> bool:
        a = self._agents.get(agent_id)
        if not a: return False
        a.status = "published"; return True
    def list_agents(self, category: Optional[str]=None) -> List[AgentAsset]:
        if category: return [a for a in self._agents.values() if category in a.capabilities]
        return list(self._agents.values())
    def count(self) -> int: return len(self._agents)
