"""Research Director v4 - distributed team formation, debate management, decision synthesis."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.agent_protocol import ResearchTask

class ResearchDirectorV4:
    def __init__(self):
        self._teams: Dict[str, List[str]] = {}; self._decisions: List[Dict[str, Any]] = []

    def form_team(self, team_id: str, agents: List[str]) -> Dict[str, Any]:
        self._teams[team_id] = agents
        return {"team_id": team_id, "agents": agents, "size": len(agents)}

    def delegate_tasks(self, team_id: str, tasks: List[ResearchTask]) -> Dict[str, Any]:
        if team_id not in self._teams: return {"error":"team not found"}
        return {"team_id": team_id, "tasks_delegated": len(tasks), "agents": self._teams[team_id]}

    def manage_debate(self, debate_results: Dict[str, Any]) -> Dict[str, Any]:
        decision = debate_results.get("decision", "undecided")
        self._decisions.append({"debate": debate_results, "decision": decision})
        return {"debate_managed": True, "decision": decision}

    def synthesize_decision(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results: return {"decision": "no_input"}
        positive = sum(1 for r in results if r.get("outcome") == "positive")
        negative = sum(1 for r in results if r.get("outcome") == "negative")
        return {"decision": "proceed" if positive > negative else "reconsider",
                "positive_votes": positive, "negative_votes": negative}

    def get_team(self, team_id: str) -> Optional[List[str]]: return self._teams.get(team_id)
    def list_decisions(self) -> List[Dict[str, Any]]: return self._decisions
