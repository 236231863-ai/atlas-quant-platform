"""Portfolio Score - diversity, coverage, correlation metrics."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.portfolio.diversity import DiversityOptimizer

@dataclass
class PortfolioResult:
    combinations: List[List[int]]; diversity_score: float; coverage_score: float
    correlation_score: float; overall_score: float; num_combinations: int
    def to_dict(self): return asdict(self)

class PortfolioScore:
    @staticmethod
    def compute(combinations: List[List[int]], total_range: int) -> PortfolioResult:
        ds = DiversityOptimizer.pairwise_diversity(combinations)
        cs = DiversityOptimizer.coverage_score(combinations, total_range)
        # Correlation score: 1 - avg similarity = diversity
        corr = 1.0 - (1.0 - ds)
        overall = round((ds * 0.4 + cs * 0.4 + (1 - corr) * 0.2), 4)
        return PortfolioResult(
            combinations=combinations, diversity_score=round(ds, 4),
            coverage_score=round(cs, 4), correlation_score=round(corr, 4),
            overall_score=overall, num_combinations=len(combinations))
