"""Research Competition System - multiple agents and strategies compete."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CompetitionReport:
    competition_id: str; type: str; participants: int; results: List[Dict[str, Any]]
    winner: str; avg_score: float = 0.0
    def to_dict(self):
        return asdict(self)

class ResearchCompetitionEngine:
    def __init__(self):
        self._competitions: List[Dict[str, Any]] = []
    def create_competition(self, comp_id: str, comp_type: str = "strategy_tournament") -> Dict[str, Any]:
        comp = {"competition_id": comp_id, "type": comp_type, "status": "created"}
        self._competitions.append(comp); return comp
    def evaluate(self, entries: List[Dict[str, Any]]) -> CompetitionReport:
        if not entries: return CompetitionReport("empty","none",0,[],"none")
        scored = []
        for e in entries:
            perf = e.get("performance", 0) * 0.4
            risk = (1 - e.get("risk", 0)) * 0.3
            innovation = e.get("innovation", 0) * 0.2
            stability = e.get("stability", 0) * 0.1
            total = perf + risk * 100 + innovation * 100 + stability * 100
            scored.append({"entry_id": e.get("entry_id","?"), "name": e.get("name","?"),
                          "total_score": round(total, 2), "performance": e.get("performance",0)})
        scored.sort(key=lambda x: x["total_score"], reverse=True)
        winner = scored[0]["name"] if scored else "none"
        avg = sum(s["total_score"] for s in scored) / len(scored) if scored else 0
        return CompetitionReport(competition_id=f"comp_{len(self._competitions)}",type="strategy_tournament",
            participants=len(entries), results=scored, winner=winner, avg_score=round(avg, 2))
    def history(self) -> List[Dict[str, Any]]: return self._competitions
