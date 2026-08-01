"""Meta Learning Layer - learn which optimizers work best."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class OptimizerRecord:
    optimizer_type: str; trials: int = 0; best_score: float = 0.0
    avg_score: float = 0.0; success_rate: float = 0.0
    def to_dict(self):
        return asdict(self)

class MetaLearner:
    def __init__(self):
        self._records: Dict[str, OptimizerRecord] = {}
        self._observations: List[Dict[str, Any]] = []

    def record_observation(self, optimizer: str, score: float, success: bool):
        if optimizer not in self._records:
            self._records[optimizer] = OptimizerRecord(optimizer_type=optimizer)
        rec = self._records[optimizer]
        rec.trials += 1
        rec.best_score = max(rec.best_score, score)
        rec.avg_score = (rec.avg_score * (rec.trials - 1) + score) / rec.trials
        rec.success_rate = (rec.success_rate * (rec.trials - 1) + (1.0 if success else 0.0)) / rec.trials
        self._observations.append({"optimizer":optimizer,"score":score,"success":success})

    def recommend(self) -> str:
        if not self._records: return "random"
        best = max(self._records.items(), key=lambda x: (x[1].avg_score, x[1].success_rate))
        return best[0]

    def get_record(self, optimizer: str) -> Optional[OptimizerRecord]:
        return self._records.get(optimizer)

    def list_records(self) -> List[OptimizerRecord]:
        return list(self._records.values())

    def performance_summary(self) -> Dict[str, Any]:
        return {opt: rec.to_dict() for opt, rec in self._records.items()}
