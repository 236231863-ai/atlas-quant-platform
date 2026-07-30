"""Research Dashboard Data Layer - structured data for visualization."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DashboardData:
    active_experiments: List[Dict[str, Any]] = field(default_factory=list)
    research_progress: Dict[str, Any] = field(default_factory=dict)
    strategy_evolution: List[Dict[str, Any]] = field(default_factory=list)
    benchmark_ranking: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_growth: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

class ResearchDashboardService:
    def __init__(self):
        self._data = DashboardData()

    def update_active_experiments(self, experiments: List[Dict[str, Any]]):
        self._data.active_experiments = experiments

    def update_research_progress(self, cycles: int, discoveries: int, experiments: int):
        self._data.research_progress = {"cycles": cycles, "discoveries": discoveries,
                                         "experiments": experiments, "completion_pct": 0.0}
        if cycles > 0: self._data.research_progress["completion_pct"] = min(100, experiments / cycles * 10)

    def update_strategy_evolution(self, strategies: List[Dict[str, Any]]):
        self._data.strategy_evolution = strategies

    def update_benchmark_ranking(self, rankings: List[Dict[str, Any]]):
        self._data.benchmark_ranking = sorted(rankings, key=lambda r: r.get("score", 0), reverse=True)

    def update_knowledge_growth(self, knowledge_count: int):
        self._data.knowledge_growth = {"total_records": knowledge_count, "growth_rate": 0.0}

    def get_data(self) -> DashboardData: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"active_experiments": len(self._data.active_experiments),
                "strategies_tracked": len(self._data.strategy_evolution),
                "benchmarks_ranked": len(self._data.benchmark_ranking),
                "knowledge_records": self._data.knowledge_growth.get("total_records", 0)}
