"""Agent Reputation System - long-term agent reliability measurement."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AgentReputation:
    agent_id: str; accuracy: float = 0.5; success_rate: float = 0.5
    prediction_quality: float = 0.5; review_rate: float = 0.5; collaboration_score: float = 0.5

    def get_rank(self) -> str:
        overall = (self.accuracy + self.success_rate + self.prediction_quality + self.review_rate + self.collaboration_score) / 5
        if overall >= 0.9: return "Master"
        elif overall >= 0.75: return "Expert"
        elif overall >= 0.6: return "Gold"
        elif overall >= 0.4: return "Silver"
        else: return "Bronze"

    def to_dict(self):
        return asdict(self)

class ReputationSystem:
    def __init__(self):
        self._reputations: Dict[str, AgentReputation] = {}
    def register(self, agent_id: str) -> AgentReputation:
        rep = AgentReputation(agent_id=agent_id); self._reputations[agent_id] = rep; return rep
    def get(self, agent_id: str) -> Optional[AgentReputation]: return self._reputations.get(agent_id)
    def increase(self, agent_id: str, field: str, amount: float = 0.05) -> bool:
        rep = self._reputations.get(agent_id)
        if not rep or not hasattr(rep, field): return False
        val = getattr(rep, field); setattr(rep, field, min(1.0, val + amount)); return True
    def decrease(self, agent_id: str, field: str, amount: float = 0.05) -> bool:
        rep = self._reputations.get(agent_id)
        if not rep or not hasattr(rep, field): return False
        val = getattr(rep, field); setattr(rep, field, max(0.0, val - amount)); return True
    def get_rank(self, agent_id: str) -> Optional[str]:
        rep = self._reputations.get(agent_id); return rep.get_rank() if rep else None
    def ranking(self) -> List[Dict[str, Any]]:
        return sorted([{"agent_id":r.agent_id,"rank":r.get_rank(),"overall":(r.accuracy+r.success_rate+r.prediction_quality+r.review_rate+r.collaboration_score)/5}
                      for r in self._reputations.values()], key=lambda x: x["overall"], reverse=True)
    def count(self) -> int: return len(self._reputations)
