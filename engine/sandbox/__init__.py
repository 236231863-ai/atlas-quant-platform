"""Experiment Sandbox System - isolated experiment environments."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class SandboxSnapshot:
    experiment_id: str; dataset_version: str = ""; strategy_id: str = ""
    model_id: str = ""; parameters: Dict[str, Any] = field(default_factory=dict)
    random_seed: Optional[int] = None; metrics: Dict[str, float] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list); created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self): return asdict(self)

class ExperimentSandbox:
    def __init__(self): self._snapshots: Dict[str, SandboxSnapshot] = {}
    def create(self, exp_id: str, params: Optional[Dict[str, Any]] = None, seed: Optional[int] = None) -> SandboxSnapshot:
        snap = SandboxSnapshot(experiment_id=exp_id, parameters=params or {}, random_seed=seed)
        self._snapshots[exp_id] = snap; return snap
    def get(self, exp_id: str) -> Optional[SandboxSnapshot]: return self._snapshots.get(exp_id)
    def clone(self, source_id: str, target_id: str) -> Optional[SandboxSnapshot]:
        src = self.get(source_id)
        if not src: return None
        snap = SandboxSnapshot(experiment_id=target_id, dataset_version=src.dataset_version,
            strategy_id=src.strategy_id, model_id=src.model_id, parameters=dict(src.parameters),
            random_seed=src.random_seed)
        self._snapshots[target_id] = snap; return snap
    def reset(self, exp_id: str) -> bool:
        if exp_id in self._snapshots:
            self._snapshots[exp_id].metrics = {}; self._snapshots[exp_id].logs = []; return True
        return False
    def compare(self, id1: str, id2: str) -> Dict[str, Any]:
        s1, s2 = self.get(id1), self.get(id2)
        if not s1 or not s2: return {"error": "Snapshot not found"}
        return {"same_dataset": s1.dataset_version == s2.dataset_version, "same_strategy": s1.strategy_id == s2.strategy_id,
                "same_params": s1.parameters == s2.parameters, "same_seed": s1.random_seed == s2.random_seed}
    def count(self) -> int: return len(self._snapshots)
