"""Growth Experiment System - A/B testing and user experience optimization."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class GrowthExperiment:
    experiment_id: str; name: str; variants: List[str]; target_metric: str
    status: str="running"; result: Dict[str, Any]=field(default_factory=dict)
    def to_dict(self): return asdict(self)

class ExperimentManager:
    def __init__(self): self._experiments: Dict[str, GrowthExperiment] = {}
    def create(self, exp: GrowthExperiment): self._experiments[exp.experiment_id]=exp; return exp
    def record_result(self, eid: str, variant: str, metric_value: float) -> bool:
        exp = self._experiments.get(eid)
        if not exp: return False
        exp.result[variant] = metric_value; exp.status = "completed"; return True
    def get_winner(self, eid: str) -> Optional[str]:
        exp = self._experiments.get(eid)
        if not exp or not exp.result: return None
        return max(exp.result, key=exp.result.get)
    def list_experiments(self) -> List[GrowthExperiment]: return list(self._experiments.values())
    def count(self) -> int: return len(self._experiments)
