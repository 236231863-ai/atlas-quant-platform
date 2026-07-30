"""Model Registry - track models, versions, parameters, datasets, metrics."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class ModelRecord:
    model_id: str; version: str; model_type: str; parameters: Dict[str, Any]
    dataset_hash: str = ""; metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "experimental"; created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    notes: str = ""
    def to_dict(self): return asdict(self)

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelRecord] = {}
        self._versions: Dict[str, List[str]] = {}
    def register(self, record: ModelRecord) -> ModelRecord:
        self._models[record.model_id] = record
        if record.model_type not in self._versions: self._versions[record.model_type] = []
        self._versions[record.model_type].append(record.model_id)
        return record
    def get(self, model_id: str) -> Optional[ModelRecord]: return self._models.get(model_id)
    def list(self) -> List[ModelRecord]: return list(self._models.values())
    def list_by_type(self, model_type: str) -> List[ModelRecord]:
        ids = self._versions.get(model_type, [])
        return [self._models[i] for i in ids if i in self._models]
    def update_metrics(self, model_id: str, metrics: Dict[str, float]) -> Optional[ModelRecord]:
        if model_id in self._models:
            self._models[model_id].metrics.update(metrics)
            return self._models[model_id]
        return None
    def update_status(self, model_id: str, status: str) -> Optional[ModelRecord]:
        if model_id in self._models:
            self._models[model_id].status = status
            return self._models[model_id]
        return None
    def search(self, **kwargs) -> List[ModelRecord]:
        results = self.list()
        for k, v in kwargs.items():
            results = [r for r in results if getattr(r, k, None) == v]
        return results
    def count(self) -> int: return len(self._models)
