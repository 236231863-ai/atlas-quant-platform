"""Research Director v5 - manage economy, competitions, resources, agent evolution."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.agent_economy import AgentEconomyEngine, AgentScore
from engine.reputation import ReputationSystem
from engine.research_competition import ResearchCompetitionEngine

class ResearchDirectorV5:
    def __init__(self):
        self._economy = AgentEconomyEngine()
        self._reputation = ReputationSystem()
        self._competition = ResearchCompetitionEngine()
        self._selected_agents: List[str] = []

    def manage_economy(self, agent_scores: List[AgentScore]) -> Dict[str, Any]:
        for s in agent_scores: self._economy.record_score(s)
        return self._economy.get_economy_metrics()

    def select_researchers(self, top_n: int = 3) -> List[Dict[str, Any]]:
        ranking = self._reputation.ranking()
        top = ranking[:top_n] if ranking else []
        self._selected_agents = [r["agent_id"] for r in top]
        return top

    def create_competition(self, comp_id: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        self._competition.create_competition(comp_id)
        report = self._competition.evaluate(entries)
        return report.to_dict() if hasattr(report, 'to_dict') else {"winner": report.winner}

    def promote_agents(self) -> List[Dict[str, Any]]:
        promotions = []
        for agent_id in self._selected_agents:
            rep = self._reputation.get(agent_id)
            if rep:
                rank = rep.get_rank()
                promotions.append({"agent_id": agent_id, "rank": rank, "promotion": rank in ["Expert", "Master"]})
        return promotions

    def get_economy(self):
        return self._economy
    def get_reputation(self):
        return self._reputation
    def get_competition(self):
        return self._competition
