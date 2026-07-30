"""Research Agent - comprehensive backtest analysis.

Takes BacktestMetrics + trade records + strategy info.
Produces structured research reports with findings.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from engine.backtest.models import BacktestMetrics, TradeRecord, BacktestConfig


@dataclass
class ResearchFinding:
    """A single research finding."""
    category: str  # performance, risk, strategy, anomaly
    severity: str  # info, warning, critical
    message: str
    metric_value: Optional[float] = None
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchReport:
    """Complete research report from analysis."""
    summary: str
    key_metrics: Dict[str, Any]
    findings: List[ResearchFinding]
    risk_assessment: Dict[str, Any]
    improvement_suggestions: List[str]
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResearchAgent:
    """Produces structured research analysis from backtest results."""

    def analyze_backtest(
        self,
        metrics: BacktestMetrics,
        trades: Optional[List[TradeRecord]] = None,
        config: Optional[BacktestConfig] = None,
    ) -> ResearchReport:
        """Analyze a single backtest result.

        Args:
            metrics: BacktestMetrics from ResultAggregator.
            trades: Full trade record list (optional, for deeper analysis).
            config: Backtest configuration (optional).

        Returns:
            ResearchReport with findings and recommendations.
        """
        findings: List[ResearchFinding] = []
        suggestions: List[str] = []

        # ROI analysis
        if metrics.roi > 0:
            findings.append(ResearchFinding(
                category="performance", severity="info",
                message=f"Positive ROI of {metrics.roi:.2f}% indicates profitable strategy.",
                metric_value=metrics.roi,
            ))
        elif metrics.roi < -50:
            findings.append(ResearchFinding(
                category="performance", severity="critical",
                message=f"Severe loss: ROI {metrics.roi:.2f}%. Strategy lost over half of capital.",
                metric_value=metrics.roi,
                recommendation="Review strategy parameters and consider reducing bet size.",
            ))
        else:
            findings.append(ResearchFinding(
                category="performance", severity="warning",
                message=f"Negative ROI of {metrics.roi:.2f}%. Strategy losing capital.",
                metric_value=metrics.roi,
            ))

        # Win rate analysis
        win_rate = metrics.win_rate
        if win_rate < 5:
            findings.append(ResearchFinding(
                category="performance", severity="warning",
                message=f"Low win rate: {win_rate:.1f}%. Few winning trades.",
                metric_value=win_rate,
                recommendation="Consider strategies with higher hit rates.",
            ))
        elif win_rate > 50:
            findings.append(ResearchFinding(
                category="performance", severity="info",
                message=f"High win rate: {win_rate:.1f}%.",
                metric_value=win_rate,
            ))

        # Sharpe analysis
        sharpe = metrics.sharpe_ratio
        if sharpe > 1.0:
            findings.append(ResearchFinding(
                category="risk", severity="info",
                message=f"Good risk-adjusted returns: Sharpe={sharpe:.2f}.",
                metric_value=sharpe,
            ))
        elif sharpe < -0.5:
            findings.append(ResearchFinding(
                category="risk", severity="critical",
                message=f"Poor risk-adjusted returns: Sharpe={sharpe:.2f}.",
                metric_value=sharpe,
                recommendation="High risk relative to returns. Reduce bet size or change strategy.",
            ))
        else:
            findings.append(ResearchFinding(
                category="risk", severity="warning",
                message=f"Mediocre risk-adjusted returns: Sharpe={sharpe:.2f}.",
                metric_value=sharpe,
            ))

        # Drawdown analysis
        dd = metrics.max_drawdown_pct
        if dd > 30:
            findings.append(ResearchFinding(
                category="risk", severity="critical",
                message=f"High max drawdown: {dd:.1f}%. Significant capital erosion risk.",
                metric_value=dd,
                recommendation="Implement drawdown stop-loss or reduce exposure.",
            ))
        elif dd > 15:
            findings.append(ResearchFinding(
                category="risk", severity="warning",
                message=f"Moderate drawdown: {dd:.1f}%.",
                metric_value=dd,
            ))
        else:
            findings.append(ResearchFinding(
                category="risk", severity="info",
                message=f"Low drawdown: {dd:.1f}%. Controlled risk.",
                metric_value=dd,
            ))

        # Volatility analysis
        vol = metrics.volatility
        if vol > 2.0:
            findings.append(ResearchFinding(
                category="risk", severity="warning",
                message=f"High volatility: {vol:.2f}. Unstable returns.",
                metric_value=vol,
            ))

        # Consecutive losses
        max_losses = metrics.max_consecutive_losses
        if max_losses > 10:
            findings.append(ResearchFinding(
                category="strategy", severity="critical",
                message=f"Long losing streak: {max_losses} consecutive losses.",
                metric_value=float(max_losses),
                recommendation="Consider pause threshold to avoid prolonged drawdowns.",
            ))
        elif max_losses > 5:
            findings.append(ResearchFinding(
                category="strategy", severity="warning",
                message=f"Notable losing streak: {max_losses} consecutive losses.",
                metric_value=float(max_losses),
            ))

        # Generate suggestions based on findings
        if metrics.roi < 0:
            suggestions.append("Consider reducing bet_per_draw to preserve capital.")
        if metrics.max_drawdown_pct > 20:
            suggestions.append("Implement maximum drawdown stop-loss at 20%.")
        if metrics.sharpe_ratio < 0:
            suggestions.append("Optimize strategy for risk-adjusted returns, not absolute returns.")
        if metrics.win_rate < 10 and metrics.roi < 0:
            suggestions.append("Explore higher-frequency strategies with better hit rates.")
        if metrics.volatility > 1.5:
            suggestions.append("Reduce position size to lower portfolio volatility.")
        if metrics.max_consecutive_losses > 8:
            suggestions.append("Add cooldown period after consecutive losses.")

        # Ensure we always have at least one suggestion
        if not suggestions:
            suggestions.append("Strategy shows balanced performance. Monitor for consistency.")

        # Key metrics summary
        key_metrics = {
            "roi": round(metrics.roi, 2),
            "win_rate": round(metrics.win_rate, 2),
            "sharpe_ratio": round(metrics.sharpe_ratio, 4),
            "max_drawdown_pct": round(metrics.max_drawdown_pct, 2),
            "volatility": round(metrics.volatility, 4),
            "total_bets": metrics.total_bets,
            "max_consecutive_losses": metrics.max_consecutive_losses,
            "avg_return_per_bet": round(metrics.avg_return_per_bet, 2),
        }

        # Overall risk assessment
        risk_score = self._compute_risk_score(metrics)
        risk_assessment = {
            "risk_score": risk_score,
            "risk_level": "low" if risk_score < 0.3 else ("medium" if risk_score < 0.6 else "high"),
            "max_drawdown_pct": round(metrics.max_drawdown_pct, 2),
            "volatility": round(metrics.volatility, 4),
        }

        summary = self._generate_summary(metrics, findings)

        return ResearchReport(
            summary=summary,
            key_metrics=key_metrics,
            findings=findings,
            risk_assessment=risk_assessment,
            improvement_suggestions=suggestions,
            confidence_score=self._compute_confidence(metrics),
        )

    def _compute_risk_score(self, metrics: BacktestMetrics) -> float:
        """Compute risk score (0-1, higher = riskier)."""
        score = 0.0
        if metrics.roi < 0:
            score += 0.3
        if metrics.max_drawdown_pct > 20:
            score += 0.3
        elif metrics.max_drawdown_pct > 10:
            score += 0.15
        if metrics.sharpe_ratio < -0.5:
            score += 0.2
        elif metrics.sharpe_ratio < 0:
            score += 0.1
        if metrics.volatility > 2.0:
            score += 0.2
        elif metrics.volatility > 1.0:
            score += 0.1
        if metrics.max_consecutive_losses > 8:
            score += 0.1
        return min(score, 1.0)

    def _compute_confidence(self, metrics: BacktestMetrics) -> float:
        """Compute confidence score based on sample size and consistency."""
        if metrics.total_bets < 10:
            return 0.3
        elif metrics.total_bets < 50:
            return 0.5
        elif metrics.total_bets < 200:
            return 0.7
        else:
            return 0.9

    def _generate_summary(
        self, metrics: BacktestMetrics, findings: List[ResearchFinding]
    ) -> str:
        """Generate a plain-text summary from metrics and findings."""
        critical = sum(1 for f in findings if f.severity == "critical")
        warnings = sum(1 for f in findings if f.severity == "warning")
        info = sum(1 for f in findings if f.severity == "info")

        lines = [
            f"Backtest analyzed {metrics.total_bets} bets.",
            f"ROI: {metrics.roi:.2f}%, Win Rate: {metrics.win_rate:.1f}%, Sharpe: {metrics.sharpe_ratio:.2f}.",
            f"Max Drawdown: {metrics.max_drawdown_pct:.1f}%, Volatility: {metrics.volatility:.3f}.",
        ]

        if critical > 0:
            lines.append(f"Found {critical} critical issues requiring attention.")
        if warnings > 0:
            lines.append(f"Found {warnings} warnings to review.")
        if info > 0:
            lines.append(f"{info} informational observations noted.")

        return " ".join(lines)

    def compare_strategies(
        self,
        strategy_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compare multiple strategy results.

        Args:
            strategy_results: List of dicts with 'strategy_id', 'name', 'metrics'.

        Returns:
            Comparison report with rankings and recommendations.
        """
        if not strategy_results:
            return {"strategies_compared": 0, "ranking": [], "recommendation": "No strategies to compare."}

        ranked = sorted(
            strategy_results,
            key=lambda r: (
                r["metrics"].sharpe_ratio if hasattr(r["metrics"], "sharpe_ratio") else r["metrics"].get("sharpe_ratio", 0)
            ),
            reverse=True,
        )

        comparisons = []
        for i, r in enumerate(ranked):
            m = r["metrics"]
            comparisons.append({
                "rank": i + 1,
                "strategy_id": r.get("strategy_id", "unknown"),
                "name": r.get("name", "Unknown"),
                "roi": round(m.roi, 2),
                "sharpe": round(m.sharpe_ratio, 4),
                "max_dd": round(m.max_drawdown_pct, 2),
            })

        best = ranked[0]
        best_name = best.get("name", best.get("strategy_id", "unknown"))
        recommendation = f"Best performing strategy: {best_name}"

        return {
            "strategies_compared": len(strategy_results),
            "ranking": comparisons,
            "recommendation": recommendation,
        }
