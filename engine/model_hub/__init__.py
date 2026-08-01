"""Model Hub System - registry, version, deployment, monitor, rollback."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ModelRecord:
    model_id:str
    name:str
    version:str="1.0"
    status:str="candidate"
    metrics:Dict[str,float]=field(default_factory=dict)
    created_at:str=""
    def to_dict(self):
        return asdict(self)

class ModelHub:
    def __init__(self):
        self._models: Dict[str, ModelRecord] = {}
        self._versions: Dict[str, List[str]] = {}
    def register(self, model: ModelRecord):
        self._models[model.model_id] = model
        return model
    def promote(self, mid: str, target: str) -> bool:
        m = self._models.get(mid)
        if not m: return False; m.status = target; return True
    def rollback(self, mid: str) -> bool:
        m = self._models.get(mid)
        if not m: return False; m.status = "candidate"; return True
    def compare(self, mid1: str, mid2: str) -> Dict[str, Any]:
        m1, m2 = self._models.get(mid1), self._models.get(mid2)
        return {"model1": m1.metrics if m1 else {}, "model2": m2.metrics if m2 else {}}
    def list_models(self) -> List[ModelRecord]: return list(self._models.values())
    def count(self) -> int: return len(self._models)
