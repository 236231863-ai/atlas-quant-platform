"""Research Scoring System - multi-dimensional experiment evaluation."""
from __future__ import annotations
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.backtest.models import BacktestMetrics

@dataclass
class ResearchScore:
    performance_score: float = 0.0; risk_score: float = 0.0; quality_score: float = 0.0
    final_score: float = 0.0; details: Dict[str, float] = field(default_factory=dict)
    def to_dict(self):
        return asdict(self)

class ResearchScoreEngine:
    @staticmethod
    def compute(metrics: BacktestMetrics, quality_factors: Optional[Dict[str, Any]] = None) -> ResearchScore:
        if metrics.total_bets == 0: return ResearchScore()
        qf = quality_factors or {}
        # Performance (0-100)
        norm_roi = max(0, min(100, (metrics.roi + 100) / 2))
        norm_sharpe = max(0, min(100, (metrics.sharpe_ratio + 3) * 20))
        perf_score = norm_roi * 0.5 + norm_sharpe * 0.5
        # Risk (0-100, higher = less risk)
        dd_score = max(0, 100 - metrics.max_drawdown_pct * 2)
        vol_score = max(0, 100 - metrics.volatility * 20)
        risk_score = dd_score * 0.6 + vol_score * 0.4
        # Quality (0-100)
        stability = qf.get("stability", 70)
        complexity = qf.get("complexity", 50)
        explainability = qf.get("explainability", 60)
        reproducibility = qf.get("reproducibility", 80)
        quality_score = (stability + (100 - complexity) + explainability + reproducibility) / 4
        # Final score (weighted)
        final_score = perf_score * 0.3 + risk_score * 0.3 + quality_score * 0.4
        return ResearchScore(performance_score=round(min(100,perf_score),2), risk_score=round(min(100,risk_score),2),
            quality_score=round(min(100,quality_score),2), final_score=round(min(100,final_score),2),
            details={"roi_norm":round(norm_roi,2),"sharpe_norm":round(norm_sharpe,2),
                     "dd_score":round(dd_score,2),"vol_score":round(vol_score,2),
                     "stability":stability,"explainability":explainability})
