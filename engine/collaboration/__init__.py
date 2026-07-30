"""Multi-Agent Collaboration System - coordinate research teams."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.agent_protocol import ResearchTask, ResearchMessage, AgentResult

@dataclass
class CollaborativeResearchReport:
    objective: str; agents_involved: List[str]; results: List[Dict[str, Any]]
    consensus: str; confidence: float
    def to_dict(self): return asdict(self)

class ResearchTeamCoordinator:
    def __init__(self):
        self._agents: Dict[str, Any] = {}; self._tasks: List[ResearchTask] = []

    def register_agent(self, agent_id: str, agent: Any):
        self._agents[agent_id] = agent

    def assign_task(self, agent_id: str, task: ResearchTask) -> bool:
        if agent_id not in self._agents: return False
        self._tasks.append(task); return True

    def collect_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        if not results: return {"status":"no_results"}
        avg_conf = sum(r.confidence for r in results) / len(results)
        return {"results_collected": len(results), "avg_confidence": round(avg_conf, 4)}

    def resolve_conflict(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not opinions: return {"decision":"no_data"}
        positive = sum(1 for o in opinions if o.get("value",0) > 0.5)
        negative = len(opinions) - positive
        return {"decision":"approved" if positive > negative else "rejected",
                "votes_for":positive,"votes_against":negative}

    def merge_conclusions(self, results: List[Dict[str, Any]]) -> str:
        return "Consensus reached: " + "; ".join(r.get("conclusion","") for r in results[:3])

    def collaborate(self, objective: str, agents: List[str]) -> CollaborativeResearchReport:
        results = []
        for aid in agents:
            if aid in self._agents:
                results.append({"agent":aid,"status":"participated"})
        return CollaborativeResearchReport(objective=objective, agents_involved=agents,
            results=results, consensus="research_completed", confidence=0.7)
