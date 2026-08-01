"""Opportunity Discovery Engine - find potential opportunities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class OpportunityRanking:
    opportunities:List[Dict[str,Any]]=field(default_factory=list)
    top_opportunity:str=""
    avg_score:float=0.0
    def to_dict(self):
        return asdict(self)

class OpportunityDiscoveryEngine:
    def __init__(self):
        self._opportunities: List[Dict[str, Any]] = []
    def register(self, name: str, opp_type: str, impact: float, probability: float, timing: float, resource: float):
        score = round((impact*0.3 + probability*0.3 + timing*0.2 + resource*0.2), 4)
        self._opportunities.append({"name": name, "type": opp_type, "impact": impact, "probability": probability,
            "timing": timing, "resource": resource, "score": score})
    def rank(self) -> OpportunityRanking:
        self._opportunities.sort(key=lambda o: o["score"], reverse=True)
        top = self._opportunities[0]["name"] if self._opportunities else ""
        avg = sum(o["score"] for o in self._opportunities)/len(self._opportunities) if self._opportunities else 0
        return OpportunityRanking(opportunities=self._opportunities, top_opportunity=top, avg_score=round(avg,4))
    def count(self) -> int: return len(self._opportunities)
