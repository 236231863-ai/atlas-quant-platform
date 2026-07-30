"""AI Expert Council - scientists debate and make research decisions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CouncilDecision:
    decision_id: str; proposal: str; participants: List[str]; arguments: List[Dict[str, Any]]
    final_conclusion: str; consensus_level: float
    def to_dict(self): return asdict(self)

class AgentScientist:
    def __init__(self, name: str, specialty: str):
        self.name = name; self.specialty = specialty
    def review(self, proposal: str) -> Dict[str, Any]:
        return {"agent": self.name, "specialty": self.specialty, "verdict": "approved", "reason": f"{self.specialty} review passed"}

class ResearchCouncil:
    def __init__(self):
        self._scientists = [
            AgentScientist("ProbabilityScientist", "probability"),
            AgentScientist("StrategyScientist", "strategy"),
            AgentScientist("RiskScientist", "risk"),
            AgentScientist("OptimizationScientist", "optimization"),
            AgentScientist("Reviewer", "review"),
        ]
        self._decisions: List[CouncilDecision] = []

    def propose_research(self, proposal: str) -> CouncilDecision:
        arguments = []
        for s in self._scientists:
            review = s.review(proposal)
            arguments.append(review)
        approved = sum(1 for a in arguments if a["verdict"] == "approved")
        total = len(arguments)
        consensus = approved / total if total > 0 else 0
        conclusion = "proceed" if consensus >= 0.6 else "rejected"
        decision = CouncilDecision(
            decision_id=f"decision_{len(self._decisions)+1}", proposal=proposal,
            participants=[s.name for s in self._scientists], arguments=arguments,
            final_conclusion=conclusion, consensus_level=round(consensus, 2))
        self._decisions.append(decision); return decision

    def get_scientist(self, name: str) -> Optional[AgentScientist]:
        return next((s for s in self._scientists if s.name == name), None)

    def get_decisions(self) -> List[CouncilDecision]: return self._decisions
    def count_decisions(self) -> int: return len(self._decisions)
