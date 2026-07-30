"""Multi Model Intelligence Layer - support multiple AI model providers."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ModelNode:
    model_id: str; provider: str; capabilities: List[str]; cost: float = 1.0
    speed: float = 1.0; quality_score: float = 0.7; status: str = "active"
    def to_dict(self): return asdict(self)

@dataclass
class ModelCapabilityProfile:
    model_id: str; provider: str; analysis_depth: int = 5; supports_streaming: bool = True
    max_context: int = 4096; modalities: List[str] = field(default_factory=lambda: ["text"])
    def to_dict(self): return asdict(self)

class ModelRegistry:
    def __init__(self): self._models: Dict[str, ModelNode] = {}; self._profiles: Dict[str, ModelCapabilityProfile] = {}
    def register(self, model: ModelNode, profile: Optional[ModelCapabilityProfile] = None):
        self._models[model.model_id] = model
        if profile: self._profiles[model.model_id] = profile
    def remove(self, model_id: str): self._models.pop(model_id, None); self._profiles.pop(model_id, None)
    def evaluate(self, model_id: str) -> Optional[float]:
        model = self._models.get(model_id)
        if not model: return None
        return round(model.quality_score * model.speed / max(model.cost, 0.01), 4)
    def select_best(self, required_capability: str) -> Optional[ModelNode]:
        candidates = [m for m in self._models.values() if required_capability in m.capabilities and m.status == "active"]
        if not candidates: return None
        return max(candidates, key=lambda m: m.quality_score)
    def list_models(self) -> List[ModelNode]: return list(self._models.values())
    def count(self) -> int: return len(self._models)
