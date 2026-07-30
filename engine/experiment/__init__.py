"""Experiment Definition Language - JSON-based experiment specification."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ExperimentDefinition:
    experiment_id: str; strategy: str = "random"; dataset: str = "default"
    features: List[str] = field(default_factory=list); optimizer: str = "none"
    parameters: Dict[str, Any] = field(default_factory=dict)
    evaluation_metrics: List[str] = field(default_factory=lambda: ["roi","sharpe_ratio"])

    def validate(self) -> List[str]:
        errors = []
        if not self.experiment_id: errors.append("experiment_id is required")
        valid_strats = ["random","cold","hot","gap_based","fixed","even","odd"]
        if self.strategy not in valid_strats: errors.append(f"Unknown strategy: {self.strategy}")
        valid_opts = ["none","bayesian","genetic","grid","random"]
        if self.optimizer not in valid_opts: errors.append(f"Unknown optimizer: {self.optimizer}")
        return errors

    def is_valid(self) -> bool: return len(self.validate()) == 0
    def serialize(self) -> str: return json.dumps(asdict(self), indent=2)
    @staticmethod
    def deserialize(data: str) -> ExperimentDefinition:
        return ExperimentDefinition(**json.loads(data))
    @staticmethod
    def compare(a: ExperimentDefinition, b: ExperimentDefinition) -> Dict[str, bool]:
        return {"same_id": a.experiment_id == b.experiment_id, "same_strategy": a.strategy == b.strategy,
                "same_dataset": a.dataset == b.dataset, "same_params": a.parameters == b.parameters}
