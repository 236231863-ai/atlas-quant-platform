"""Experiment Execution Engine - run experiments end to end."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

@dataclass
class ExecutionResult:
    experiment_id: str; success: bool; metrics: Dict[str, float] = field(default_factory=dict)
    error: str = ""; execution_time: float = 0.0; log: List[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

class ExperimentRunner:
    def __init__(self):
        self._dataset_fn: Optional[Callable] = None
        self._strategy_fn: Optional[Callable] = None
        self._feature_fn: Optional[Callable] = None
        self._backtest_fn: Optional[Callable] = None

    def set_dataset_fn(self, fn: Callable): self._dataset_fn = fn
    def set_strategy_fn(self, fn: Callable): self._strategy_fn = fn
    def set_feature_fn(self, fn: Callable): self._feature_fn = fn
    def set_backtest_fn(self, fn: Callable): self._backtest_fn = fn

    def run_single(self, exp_id: str, params: Dict[str, Any]) -> ExecutionResult:
        log = [f"Starting experiment {exp_id}"]
        try:
            if self._strategy_fn: self._strategy_fn(params); log.append("Strategy loaded")
            if self._feature_fn: self._feature_fn(params); log.append("Features generated")
            metrics = {}
            if self._backtest_fn:
                result = self._backtest_fn(params)
                if isinstance(result, dict): metrics = result
                log.append("Backtest completed")
            return ExecutionResult(experiment_id=exp_id, success=True, metrics=metrics, log=log)
        except Exception as e:
            log.append(f"Error: {e}")
            return ExecutionResult(experiment_id=exp_id, success=False, error=str(e), log=log)

    def run_batch(self, experiments: List[Tuple[str, Dict[str, Any]]]) -> List[ExecutionResult]:
        return [self.run_single(eid, params) for eid, params in experiments]

    def parallel_config(self, max_workers: int = 4) -> Dict[str, Any]:
        return {"max_workers": max_workers, "strategy": "thread_pool"}
