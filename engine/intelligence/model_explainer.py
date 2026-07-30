"""Model Explainer - explains strategy performance, feature contributions."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from engine.backtest.models import BacktestMetrics, TradeRecord
from engine.strategy.registry import StrategyDefinition


@dataclass
class FeatureImportance:
    """Feature importance analysis."""
    feature_name: str
    importance_score: float
    direction: str  # positive, negative, neutral
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelExplainer:
    """Explains strategy behavior, performance, and feature contributions.

    Pure computation analysis of strategy results.
    """

    def analyze_performance(
        self,
        metrics: BacktestMetrics,
        trades: List[TradeRecord],
        strategy: Optional[StrategyDefinition] = None,
    ) -> Dict[str, Any]:
        """Analyze and explain why a strategy performed as it did.

        Args:
            metrics: Backtest metrics.
            trades: Trade records from backtest.
            strategy: Strategy definition (optional).

        Returns:
            Structured explanation with attribution and factors.
        """
        if not trades:
            return {"strategy_id": strategy.strategy_id if strategy else "unknown", "explanation": "No trades to analyze."}

        # Analyze win/loss distribution
        win_trades = [t for t in trades if t.is_win]
        loss_trades = [t for t in trades if not t.is_win]

        # Average win vs loss amounts
        avg_win = sum(t.win_amount for t in win_trades) / len(win_trades) if win_trades else 0
        avg_loss = sum(t.bet_amount for t in loss_trades) / len(loss_trades) if loss_trades else 0

        # Prize level distribution
        prize_dist = Counter(t.prize_level for t in win_trades)

        # Winning patterns - which prize levels contributed most to returns
        win_contributions = []
        for level, count in prize_dist.most_common():
            level_trades = [t for t in win_trades if t.prize_level == level]
            total_won = sum(t.win_amount for t in level_trades)
            pct_of_total = (total_won / metrics.total_return * 100) if metrics.total_return > 0 else 0
            win_contributions.append({
                "prize_level": level,
                "count": count,
                "total_won": round(total_won, 2),
                "pct_of_total_return": round(pct_of_total, 1),
            })

        # Explanatory factors
        factors = self._compute_performance_factors(metrics, trades)

        return {
            "strategy_id": strategy.strategy_id if strategy else "unknown",
            "overall": {
                "total_trades": len(trades),
                "win_trades": len(win_trades),
                "loss_trades": len(loss_trades),
                "avg_win_amount": round(avg_win, 2),
                "avg_loss_amount": round(avg_loss, 2),
                "profit_factor": round(metrics.total_return / metrics.total_investment, 4) if metrics.total_investment > 0 else 0,
            },
            "win_contributions": win_contributions,
            "performance_factors": factors,
        }

    def _compute_performance_factors(
        self, metrics: BacktestMetrics, trades: List[TradeRecord]
    ) -> List[Dict[str, Any]]:
        """Compute explanatory factors for strategy performance."""
        factors = []

        # Factor 1: Win rate
        factors.append({
            "factor": "win_rate",
            "value": round(metrics.win_rate, 1),
            "interpretation": "High" if metrics.win_rate > 40 else ("Moderate" if metrics.win_rate > 15 else "Low"),
            "impact": "positive" if metrics.win_rate > 30 else "negative",
        })

        # Factor 2: Risk-reward ratio
        win_trades = [t for t in trades if t.is_win]
        loss_trades = [t for t in trades if not t.is_win]
        avg_win = sum(t.win_amount for t in win_trades) / len(win_trades) if win_trades else 0
        avg_loss = sum(t.bet_amount for t in loss_trades) / len(loss_trades) if loss_trades else 0
        rr_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        factors.append({
            "factor": "risk_reward_ratio",
            "value": round(rr_ratio, 2),
            "interpretation": "Good" if rr_ratio > 2 else ("Fair" if rr_ratio > 1 else "Poor"),
            "impact": "positive" if rr_ratio > 1.5 else "negative",
        })

        # Factor 3: Consistency (std of returns)
        volatility_impact = "high_risk" if metrics.volatility > 2.0 else ("moderate_risk" if metrics.volatility > 1.0 else "stable")
        factors.append({
            "factor": "consistency",
            "value": round(metrics.volatility, 4),
            "interpretation": "Stable" if metrics.volatility < 1.0 else "Volatile",
            "impact": volatility_impact,
        })

        # Factor 4: Drawdown severity
        factors.append({
            "factor": "drawdown_severity",
            "value": round(metrics.max_drawdown_pct, 1),
            "interpretation": "Controlled" if metrics.max_drawdown_pct < 15 else ("Significant" if metrics.max_drawdown_pct < 30 else "Severe"),
            "impact": "negative" if metrics.max_drawdown_pct > 15 else "neutral",
        })

        return factors

    def compute_feature_importance(
        self,
        trades: List[TradeRecord],
        metrics: BacktestMetrics,
    ) -> List[FeatureImportance]:
        """Analyze which features/patterns contributed most to performance.

        Pure computation: derives importance from trade pattern analysis.

        Returns:
            List of FeatureImportance items sorted by importance.
        """
        if not trades:
            return []

        importance: List[FeatureImportance] = []

        # Feature 1: Prize level hit rate importance
        prize_hits = Counter(t.prize_level for t in trades if t.is_win)
        total_wins = sum(prize_hits.values())
        if total_wins > 0:
            high_prize_pct = sum(v for k, v in prize_hits.items() if k <= 3) / total_wins * 100
            importance.append(FeatureImportance(
                feature_name="high_prize_hits",
                importance_score=round(high_prize_pct / 100, 4),
                direction="positive" if high_prize_pct > 20 else "neutral",
                description=f"{high_prize_pct:.1f}% of wins are high-value prizes (level 1-3)",
            ))

        # Feature 2: Win frequency importance
        wr = metrics.win_rate
        importance.append(FeatureImportance(
            feature_name="win_frequency",
            importance_score=round(wr / 100, 4),
            direction="positive" if wr > 20 else "negative" if wr < 5 else "neutral",
            description=f"Strategy wins {wr:.1f}% of the time",
        ))

        # Feature 3: Drawdown control
        dd = metrics.max_drawdown_pct
        dd_score = max(0, 1 - dd / 50)  # 0% DD = 1.0, 50% DD = 0.0
        importance.append(FeatureImportance(
            feature_name="drawdown_control",
            importance_score=round(dd_score, 4),
            direction="positive" if dd < 15 else "negative" if dd > 25 else "neutral",
            description=f"Maximum drawdown of {dd:.1f}%",
        ))

        # Feature 4: Risk-adjusted returns
        sharpe_score = max(0, min(1, (metrics.sharpe_ratio + 2) / 4))  # Map -2..2 to 0..1
        importance.append(FeatureImportance(
            feature_name="risk_adjusted_returns",
            importance_score=round(sharpe_score, 4),
            direction="positive" if metrics.sharpe_ratio > 0.5 else "negative" if metrics.sharpe_ratio < -0.5 else "neutral",
            description=f"Sharpe ratio of {metrics.sharpe_ratio:.2f}",
        ))

        # Sort by importance score descending
        importance.sort(key=lambda x: x.importance_score, reverse=True)
        return importance

    def generate_explanation(
        self,
        metrics: BacktestMetrics,
        importance: List[FeatureImportance],
    ) -> str:
        """Generate a plain-text explanation of strategy performance.

        Args:
            metrics: Backtest metrics.
            importance: Feature importance analysis.

        Returns:
            Human-readable explanation string.
        """
        lines: List[str] = []

        if metrics.roi > 0:
            lines.append(f"The strategy produced a positive return of {metrics.roi:.2f}%.")
        else:
            lines.append(f"The strategy produced a negative return of {metrics.roi:.2f}%.")

        if importance:
            top = importance[0]
            lines.append(f"The most important factor was '{top.feature_name}' (score: {top.importance_score:.2f}).")

            if importance[0].direction == "positive":
                lines.append("Key positive factors contributed to performance.")
            elif any(f.direction == "negative" for f in importance[:3]):
                neg_factors = [f.feature_name for f in importance[:3] if f.direction == "negative"]
                lines.append(f"Areas for improvement: {', '.join(neg_factors)}.")

        lines.append(f"Total of {metrics.total_bets} bets were analyzed for this explanation.")

        return " ".join(lines)
