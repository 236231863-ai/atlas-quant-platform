"""Massive Experiment Engine - large scale batch execution."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class BatchExperimentReport:
    batch_id: str; total_experiments: int; results: List[Dict[str, Any]]
    success_rate: float = 0.0; avg_score: float = 0.0
    def to_dict(self): return asdict(self)

class ExperimentBatchEngine:
    def __init__(self):
        self._batch_counter = 0; self._experiments: List[Dict[str, Any]] = []

    def create_batch(self, count: int, base_params: Dict[str, Any], param_variations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._batch_counter += 1
        experiments = []
        for i in range(min(count, len(param_variations) or 1)):
            params = dict(base_params)
            if i < len(param_variations): params.update(param_variations[i])
            experiments.append({"experiment_id": f"batch_{self._batch_counter}_exp_{i+1}",
                                "params": params, "group": f"batch_{self._batch_counter}"})
        self._experiments.extend(experiments)
        return experiments

    def group_by_strategy(self) -> Dict[str, List[Dict[str, Any]]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for e in self._experiments:
            strat = str(e.get("params", {}).get("strategy", "unknown"))
            if strat not in groups: groups[strat] = []
            groups[strat].append(e)
        return groups

    def aggregate_results(self, results: List[Dict[str, Any]]) -> BatchExperimentReport:
        if not results: return BatchExperimentReport("empty", 0, [], 0.0, 0.0)
        success = sum(1 for r in results if r.get("success", False))
        scores = [r.get("score", 0) for r in results if "score" in r]
        return BatchExperimentReport(
            batch_id=f"batch_{self._batch_counter}", total_experiments=len(results),
            results=results, success_rate=round(success/len(results), 4) if results else 0,
            avg_score=round(sum(scores)/len(scores), 4) if scores else 0)

    def parallel_config(self, max_workers: int = 4) -> Dict[str, Any]:
        return {"max_workers": max_workers, "batch_size": min(100, max_workers * 10)}
