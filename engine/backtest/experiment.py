"""Atlas Quant Platform - Experiment Management.

Tracks experiment metadata, strategy versions, and backtest runs.
Pure data structures, no persistence.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from engine.backtest.models import BacktestMetrics


@dataclass
class StrategyVersion:
    """Tracks version history of a strategy definition."""
    strategy_id: str
    version: int
    parameters: Dict[str, Any]
    parent_version: Optional[int] = None
    change_description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentResult:
    """Result of a single experiment (one backtest run with metadata)."""
    experiment_id: str
    strategy_id: str
    strategy_version: int
    parameters: Dict[str, Any]
    config_summary: Dict[str, Any]
    metrics: BacktestMetrics
    feature_set: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "strategy_id": self.strategy_id,
            "strategy_version": self.strategy_version,
            "parameters": self.parameters,
            "config_summary": self.config_summary,
            "metrics": self.metrics.to_dict(),
            "feature_set": self.feature_set,
            "created_at": self.created_at,
        }


class ExperimentTracker:
    """Manages experiment records and strategy versions."""

    def __init__(self) -> None:
        self._experiments: List[ExperimentResult] = []
        self._versions: Dict[str, List[StrategyVersion]] = {}

    def record_experiment(self, result: ExperimentResult) -> None:
        self._experiments.append(result)

    def record_version(self, version: StrategyVersion) -> None:
        if version.strategy_id not in self._versions:
            self._versions[version.strategy_id] = []
        self._versions[version.strategy_id].append(version)

    def get_experiments(self, strategy_id: Optional[str] = None) -> List[ExperimentResult]:
        if strategy_id:
            return [e for e in self._experiments if e.strategy_id == strategy_id]
        return self._experiments.copy()

    def get_best_by_metric(self, metric: str = "sharpe_ratio", top_n: int = 5) -> List[ExperimentResult]:
        """Get top N experiments sorted by a metric."""
        sorted_exps = sorted(
            self._experiments,
            key=lambda e: getattr(e.metrics, metric, 0),
            reverse=True,
        )
        return sorted_exps[:top_n]

    def get_versions(self, strategy_id: str) -> List[StrategyVersion]:
        return self._versions.get(strategy_id, [])

    def count_experiments(self) -> int:
        return len(self._experiments)

    def clear(self) -> None:
        self._experiments.clear()
        self._versions.clear()
