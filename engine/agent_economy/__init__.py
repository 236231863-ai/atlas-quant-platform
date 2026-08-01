"""Agent Economy Foundation - measurable value system for agents."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AgentScore:
    agent_id: str; performance_score: float = 0.0; contribution_score: float = 0.0
    knowledge_score: float = 0.0; overall_score: float = 0.0
    def compute(self):
        self.overall_score = round((self.performance_score * 0.4 + self.contribution_score * 0.3 + self.knowledge_score * 0.3), 4)
    def to_dict(self):
        return asdict(self)

class AgentEconomyEngine:
    def __init__(self):
        self._scores: Dict[str, List[AgentScore]] = {}
    def record_score(self, score: AgentScore):
        score.compute()
        if score.agent_id not in self._scores: self._scores[score.agent_id] = []
        self._scores[score.agent_id].append(score)
    def get_scores(self, agent_id: str) -> List[AgentScore]: return self._scores.get(agent_id, [])
    def get_latest(self, agent_id: str) -> Optional[AgentScore]:
        scores = self._scores.get(agent_id, []); return scores[-1] if scores else None
    def get_economy_metrics(self) -> Dict[str, Any]:
        all_scores = [s for scores in self._scores.values() for s in scores]
        if not all_scores: return {"total_agents":0,"avg_performance":0,"avg_contribution":0,"avg_overall":0}
        return {"total_agents": len(self._scores), "total_records": len(all_scores),
                "avg_performance": round(sum(s.performance_score for s in all_scores)/len(all_scores),4),
                "avg_contribution": round(sum(s.contribution_score for s in all_scores)/len(all_scores),4)}
