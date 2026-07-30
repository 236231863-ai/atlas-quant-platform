"""Model Training Pipeline - dataset to trained model to registry."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Callable

@dataclass
class TrainingRun:
    run_id: str; model_id: str; dataset_version: str; parameters: Dict[str, Any]
    metrics: Dict[str, float] = field(default_factory=dict); status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""
    def to_dict(self): return asdict(self)

class TrainingPipeline:
    def __init__(self):
        self._runs: Dict[str, TrainingRun] = {}
        self._feature_fn: Optional[Callable] = None
        self._train_fn: Optional[Callable] = None
        self._eval_fn: Optional[Callable] = None

    def set_feature_fn(self, fn: Callable): self._feature_fn = fn
    def set_train_fn(self, fn: Callable): self._train_fn = fn
    def set_eval_fn(self, fn: Callable): self._eval_fn = fn

    def create_run(self, run_id: str, model_id: str, dataset_version: str, params: Dict[str, Any]) -> TrainingRun:
        run = TrainingRun(run_id=run_id, model_id=model_id, dataset_version=dataset_version, parameters=params)
        self._runs[run_id] = run; return run

    def execute(self, run_id: str, raw_data: List[Any]) -> Optional[TrainingRun]:
        run = self._runs.get(run_id)
        if not run: return None
        run.status = "running"
        try:
            features = self._feature_fn(raw_data) if self._feature_fn else raw_data
            model = self._train_fn(features) if self._train_fn else None
            metrics = self._eval_fn(features, model) if self._eval_fn and model else {}
            run.metrics.update(metrics)
            run.status = "completed"
        except Exception as e:
            run.status = "failed"; run.notes = str(e)
        return run

    def get_run(self, run_id: str) -> Optional[TrainingRun]: return self._runs.get(run_id)
    def list_runs(self) -> List[TrainingRun]: return list(self._runs.values())
    def list_by_status(self, status: str) -> List[TrainingRun]:
        return [r for r in self._runs.values() if r.status == status]
    def count(self) -> int: return len(self._runs)
