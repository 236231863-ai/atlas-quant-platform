"""Strategy Advisor - generates improvement suggestions and risk warnings."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from engine.backtest.models import BacktestMetrics, TradeRecord
from engine.strategy.registry import StrategyDefinition


@dataclass
class AdvisorSuggestion:
    """A single advisor suggestion."""
    category: str  # weight_adjustment, risk_warning, improvement
    priority: str  # high, medium, low
    message: str
    expected_impact: str  # positive, neutral, unknown
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StrategyAdvisor:
    """Generates data-driven strategy improvement suggestions.

    Pure computation: analyzes metrics and trade history to recommend changes.
    """

    def analyze(
        self,
        metrics: BacktestMetrics,
        trades: List[TradeRecord],
        strategy: Optional[StrategyDefinition] = None,
    ) -> List[AdvisorSuggestion]:
        """Generate suggestions for strategy improvement.

        Args:
            metrics: Backtest metrics.
            trades: Trade records from backtest.
            strategy: Current strategy definition (optional).

        Returns:
            List of suggestions sorted by priority.
        """
        suggestions: List[AdvisorSuggestion] = []

        # 1. Risk warnings
        if metrics.max_drawdown_pct > 25:
            suggestions.append(AdvisorSuggestion(
                category="risk_warning", priority="high",
                message=f"Drawdown of {metrics.max_drawdown_pct:.1f}% exceeds 25% threshold. "
                        f"Consider implementing a stop-loss mechanism.",
                expected_impact="positive",
                details={"current_drawdown": round(metrics.max_drawdown_pct, 1), "threshold": 25},
            ))
        elif metrics.max_drawdown_pct > 15:
            suggestions.append(AdvisorSuggestion(
                category="risk_warning", priority="medium",
                message=f"Drawdown of {metrics.max_drawdown_pct:.1f}% is notable. Monitor closely.",
                expected_impact="positive",
                details={"current_drawdown": round(metrics.max_drawdown_pct, 1), "threshold": 15},
            ))

        if metrics.volatility > 2.0:
            suggestions.append(AdvisorSuggestion(
                category="risk_warning", priority="high",
                message=f"Volatility of {metrics.volatility:.2f} is high. Consider reducing bet size by 50%.",
                expected_impact="positive",
                details={"current_volatility": round(metrics.volatility, 4), "suggested_reduction": 0.5},
            ))

        if metrics.max_consecutive_losses > 8:
            suggestions.append(AdvisorSuggestion(
                category="risk_warning", priority="high",
                message=f"Strategy had {metrics.max_consecutive_losses} consecutive losses. "
                        f"Implement cooldown after 5 consecutive losses.",
                expected_impact="positive",
            ))

        # 2. Weight adjustments
        if metrics.win_rate < 10 and metrics.roi < 0:
            suggestions.append(AdvisorSuggestion(
                category="weight_adjustment", priority="high",
                message=f"Low win rate ({metrics.win_rate:.1f}%) combined with negative returns. "
                        f"Consider switching to a different strategy type.",
                expected_impact="positive",
            ))

        if metrics.roi < -30:
            suggestions.append(AdvisorSuggestion(
                category="weight_adjustment", priority="high",
                message=f"Severe losses ({metrics.roi:.1f}%). Reduce bet_per_draw by 50% to preserve capital.",
                expected_impact="positive",
                details={"current_bet_reduction": 0.5},
            ))

        if metrics.sharpe_ratio < -0.5 and metrics.roi < 0:
            suggestions.append(AdvisorSuggestion(
                category="weight_adjustment", priority="medium",
                message=f"Negative Sharpe ({metrics.sharpe_ratio:.2f}) indicates poor risk-adjusted returns. "
                        f"Optimize for Sharpe ratio rather than absolute return.",
                expected_impact="positive",
            ))

        # 3. Improvements
        if metrics.total_bets > 0:
            suggestions.append(AdvisorSuggestion(
                category="improvement", priority="medium",
                message=f"Analyzed {metrics.total_bets} trades. "
                        f"Increase sample size for more robust conclusions.",
                expected_impact="neutral",
            ))

        if metrics.roi > 0 and metrics.sharpe_ratio > 1.0:
            suggestions.append(AdvisorSuggestion(
                category="improvement", priority="low",
                message=f"Strategy shows positive returns with good risk metrics. "
                        f"Consider A/B testing parameter variations to further optimize.",
                expected_impact="positive",
            ))

        if metrics.max_consecutive_losses > 5:
            suggestions.append(AdvisorSuggestion(
                category="improvement", priority="medium",
                message=f"Longest losing streak was {metrics.max_consecutive_losses}. "
                        f"Add a pause-skip rule: skip betting after 5 consecutive losses.",
                expected_impact="positive",
            ))

        # Ensure suggestions exist
        if not suggestions:
            suggestions.append(AdvisorSuggestion(
                category="improvement", priority="low",
                message="Strategy performance is within normal parameters. Continue monitoring.",
                expected_impact="neutral",
            ))

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 99))
        return suggestions

    def suggest_weight_adjustments(
        self,
        strategy: StrategyDefinition,
        metrics: BacktestMetrics,
    ) -> List[AdvisorSuggestion]:
        """Suggest weight adjustments for composite strategies.

        Args:
            strategy: Current strategy definition.
            metrics: Backtest metrics.

        Returns:
            Weight adjustment suggestions.
        """
        suggestions: List[AdvisorSuggestion] = []
        params = strategy.params or {}

        if strategy.strategy_type == "gap_based":
            min_gap = params.get("min_gap", 5)
            if metrics.roi < -20:
                suggestions.append(AdvisorSuggestion(
                    category="weight_adjustment", priority="high",
                    message=f"Current min_gap={min_gap} not producing results. "
                            f"Try adjusting min_gap to {min(min_gap + 5, 30)} or switch to hot strategy.",
                    expected_impact="positive",
                ))
            elif metrics.roi > 0 and metrics.sharpe_ratio < 0.5:
                suggestions.append(AdvisorSuggestion(
                    category="weight_adjustment", priority="medium",
                    message=f"Strategy is profitable but risk-adjusted returns are low (Sharpe={metrics.sharpe_ratio:.2f}). "
                            f"Consider combining with additional filters.",
                    expected_impact="positive",
                ))

        if strategy.strategy_type == "hot" and metrics.roi < -10:
            suggestions.append(AdvisorSuggestion(
                category="weight_adjustment", priority="medium",
                message="Hot number strategy underperforming. Hot numbers may be overvalued. "
                        "Consider switching to cold or gap-based strategy.",
                expected_impact="positive",
            ))

        if not suggestions:
            suggestions.append(AdvisorSuggestion(
                category="improvement", priority="low",
                message="No weight adjustments needed at this time.",
                expected_impact="neutral",
            ))

        return suggestions
