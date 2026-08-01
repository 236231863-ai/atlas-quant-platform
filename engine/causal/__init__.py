"""Causal Intelligence Engine - causal analysis, graphs, counterfactual reasoning."""
from __future__ import annotations
import math, random
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class CounterfactualReport:
    scenario:str
    cause:str
    predicted_outcome:str
    confidence:float=0.5
    impact_score:float=0.0
    def to_dict(self):
        return asdict(self)

class CausalGraph:
    def __init__(self):
        self._nodes: Dict[str, List[Tuple[str, float]]] = {}
    def add_edge(self, cause: str, effect: str, strength: float = 0.5):
        if cause not in self._nodes: self._nodes[cause] = []
        self._nodes[cause].append((effect, strength))
    def get_effects(self, cause: str) -> List[Tuple[str, float]]: return self._nodes.get(cause, [])
    def count_edges(self) -> int: return sum(len(v) for v in self._nodes.values())
    def count_nodes(self) -> int: return len(self._nodes)

class CausalAnalyzer:
    @staticmethod
    def analyze(cause: str, effect: str, observations: List[Tuple[float, float]]) -> Dict[str, float]:
        if len(observations) < 3: return {"cause_score": 0.0, "impact_score": 0.0, "confidence": 0.0}
        cause_vals = [o[0] for o in observations]; effect_vals = [o[1] for o in observations]
        n = len(cause_vals); mx = sum(cause_vals)/n; my = sum(effect_vals)/n
        num = sum((cause_vals[i]-mx)*(effect_vals[i]-my) for i in range(n))
        den = math.sqrt(sum((cause_vals[i]-mx)**2 for i in range(n)))*math.sqrt(sum((effect_vals[i]-my)**2 for i in range(n)))
        corr = num/den if den>0 else 0
        return {"cause_score": round(abs(corr),4), "impact_score": round(abs(corr)*10,4), "confidence": round(abs(corr),4)}

class CounterfactualEngine:
    @staticmethod
    def simulate(cause: str, action: str, current_state: Dict[str, Any]) -> CounterfactualReport:
        impact = 0.5 if action == "increase" else (-0.5 if action == "decrease" else 0.0)
        return CounterfactualReport(scenario=f"If we {action} {cause}", cause=cause,
            predicted_outcome=f"Impact of {impact:.1f} on related variables", confidence=0.6, impact_score=abs(impact))
