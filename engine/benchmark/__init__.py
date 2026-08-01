"""Research Benchmark System - scientific strategy evaluation."""
from __future__ import annotations
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.backtest.models import BacktestMetrics

@dataclass
class BenchmarkScore:
    performance: float = 0.0; risk: float = 0.0; quality: float = 0.0
    generalization: float = 0.0; final_score: float = 0.0
    def to_dict(self):
        return asdict(self)

class ResearchBenchmarkEngine:
    @staticmethod
    def compute(metrics: BacktestMetrics, cv_scores: Optional[List[float]] = None,
                quality_factors: Optional[Dict[str, Any]] = None) -> BenchmarkScore:
        if metrics.total_bets == 0: return BenchmarkScore()
        qf = quality_factors or {}
        perf = max(0, min(100, (metrics.roi + 100) / 2)) * 0.5 + max(0, min(100, (metrics.sharpe_ratio + 3) * 20)) * 0.5
        risk = max(0, 100 - metrics.max_drawdown_pct * 2) * 0.6 + max(0, 100 - metrics.volatility * 20) * 0.4
        quality = (qf.get("stability",70) + (100 - qf.get("complexity",50)) + qf.get("explainability",60) + qf.get("reproducibility",80)) / 4
        gen = sum(cv_scores)/len(cv_scores) * 100 if cv_scores else 50
        final = perf * 0.25 + risk * 0.25 + quality * 0.25 + gen * 0.25
        return BenchmarkScore(performance=round(min(100,perf),2), risk=round(min(100,risk),2),
            quality=round(min(100,quality),2), generalization=round(min(100,gen),2), final_score=round(min(100,final),2))

    @staticmethod
    def cross_validate(roi_values: List[float], n_folds: int = 5) -> List[float]:
        if len(roi_values) < n_folds: return [sum(roi_values)/len(roi_values)] if roi_values else [0.0]
        fold_size = len(roi_values) // n_folds
        scores = []
        for i in range(n_folds):
            test = roi_values[i*fold_size:(i+1)*fold_size]
            train = roi_values[:i*fold_size] + roi_values[(i+1)*fold_size:]
            train_mean = sum(train)/len(train) if train else 0
            test_mean = sum(test)/len(test) if test else 0
            scores.append(1 - abs(train_mean - test_mean) / (abs(train_mean) + 0.01))
        return scores
