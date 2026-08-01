"""Agent Contribution Economy - measure and reward AI scientist contributions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AgentContribution:
    agent_id: str; research_score: float = 0.0; knowledge_score: float = 0.0
    innovation_score: float = 0.0; reward: float = 0.0
    def overall(self):
        return round((self.research_score+self.knowledge_score+self.innovation_score)/3, 4)
    def to_dict(self):
        return asdict(self)

class ContributionRewardEngine:
    def __init__(self):
        self._contributions: Dict[str, AgentContribution] = {}
    def calculate(self, contrib: AgentContribution):
        contrib.reward = round(contrib.overall() * 100, 2)
        self._contributions[contrib.agent_id] = contrib; return contrib
    def rank(self) -> List[Dict[str, Any]]:
        sorted_c = sorted(self._contributions.values(), key=lambda c: c.reward, reverse=True)
        return [{"agent_id": c.agent_id, "reward": c.reward} for c in sorted_c]
    def generate_bonus(self, agent_id: str, multiplier: float = 1.0) -> Optional[float]:
        contrib = self._contributions.get(agent_id)
        if not contrib: return None
        return round(contrib.reward * multiplier, 2)
    def get_contribution(self, agent_id: str) -> Optional[AgentContribution]: return self._contributions.get(agent_id)
    def count(self) -> int: return len(self._contributions)
