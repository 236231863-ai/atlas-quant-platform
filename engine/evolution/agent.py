"""Agent Evolution Engine - allow agents to improve over time."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AgentVersion:
    agent_id: str; version: int; skills: Dict[str, float]; parameters: Dict[str, Any]
    performance: Dict[str, float] = field(default_factory=dict); parent_version: Optional[int] = None
    def to_dict(self): return asdict(self)

class AgentEvolutionEngine:
    def __init__(self): self._versions: Dict[str, List[AgentVersion]] = {}
    def record_version(self, v: AgentVersion):
        if v.agent_id not in self._versions: self._versions[v.agent_id] = []
        self._versions[v.agent_id].append(v)
    def get_versions(self, agent_id: str) -> List[AgentVersion]: return self._versions.get(agent_id, [])
    def skill_mutation(self, agent_id: str, skills: Dict[str, float], factor: float = 0.1) -> AgentVersion:
        versions = self._versions.get(agent_id, [])
        parent_v = versions[-1].version if versions else 0
        new_skills = {k: min(1.0, v * (1 + factor)) for k, v in skills.items()}
        v = AgentVersion(agent_id=agent_id, version=parent_v + 1, skills=new_skills, parameters={}, parent_version=parent_v if parent_v > 0 else None)
        self.record_version(v); return v
    def latest_version(self, agent_id: str) -> Optional[AgentVersion]:
        versions = self._versions.get(agent_id, []); return versions[-1] if versions else None
    def evolution_history(self, agent_id: str) -> List[AgentVersion]:
        return self._versions.get(agent_id, [])
