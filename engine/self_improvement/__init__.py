"""Self Improvement System - evaluate, detect, improve."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CapabilityMetrics:
    research_efficiency: float = 0.5; knowledge_growth: float = 0.5
    agent_capability: float = 0.5; experiment_quality: float = 0.5
    def overall(self) -> float: return round((self.research_efficiency+self.knowledge_growth+self.agent_capability+self.experiment_quality)/4, 4)
    def to_dict(self): return asdict(self)

class SelfImprovementEngine:
    def __init__(self):
        self._metrics_history: List[CapabilityMetrics] = []
        self._improvements: List[str] = []

    def evaluate_capability(self, metrics: CapabilityMetrics) -> CapabilityMetrics:
        self._metrics_history.append(metrics); return metrics

    def detect_weakness(self) -> Optional[str]:
        if not self._metrics_history: return None
        latest = self._metrics_history[-1]
        metrics_map = {"research_efficiency": latest.research_efficiency,
                       "knowledge_growth": latest.knowledge_growth,
                       "agent_capability": latest.agent_capability,
                       "experiment_quality": latest.experiment_quality}
        weakest = min(metrics_map, key=metrics_map.get)
        if metrics_map[weakest] < 0.4: return weakest
        return None

    def generate_improvement_goal(self, weakness: str) -> str:
        goal = f"Improve {weakness} from current level to target level"
        self._improvements.append(goal); return goal

    def get_history(self) -> List[CapabilityMetrics]: return self._metrics_history
    def get_improvements(self) -> List[str]: return self._improvements
    def count_metrics(self) -> int: return len(self._metrics_history)
