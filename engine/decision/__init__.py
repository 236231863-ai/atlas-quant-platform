"""Decision Simulation Engine - simulate and compare decision outcomes."""
from __future__ import annotations
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DecisionReport:
    goal:str
    scenarios:List[Dict[str,Any]]
    recommended:str=""
    confidence:float=0.0
    def to_dict(self):
        return asdict(self)

class DecisionSimulator:
    @staticmethod
    def simulate(goal: str, actions: List[Dict[str, Any]], seed: Optional[int]=None) -> DecisionReport:
        rng = random.Random(seed); scenarios = []
        for action in actions:
            risk = rng.random() * 0.5; reward = rng.random() * action.get("investment", 1)
            scenarios.append({"action": action.get("name","?"), "risk": round(risk,2), "expected_reward": round(reward,2),
                "score": round(reward/(risk+0.01),2)})
        scenarios.sort(key=lambda s: s["score"], reverse=True)
        best = scenarios[0] if scenarios else {}
        return DecisionReport(goal=goal, scenarios=scenarios, recommended=best.get("action",""), confidence=round(best.get("score",0)/max(s["score"] for s in scenarios) if scenarios else 0, 2))
