"""Atlas Quant Platform - AI Research Upgrade.

Enhanced ResearchAgent with probability explanation, model comparison, experiment recommendations.
Pure computation: consumes structured data from Engine.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from engine.backtest.models import BacktestMetrics


def explain_probability(bayesian_results: List[Dict[str, Any]], markov_results: List[Dict[str, Any]]) -> str:
    """Generate natural-language explanation of probability analysis results."""
    lines = ["## Probability Analysis Summary", ""]
    if bayesian_results:
        sorted_b = sorted(bayesian_results, key=lambda r: r.get("probability_change", 0), reverse=True)
        if sorted_b:
            top = sorted_b[0]
            lines.append(f"Number {top['number']} shows highest probability change of {top.get('probability_change',0):.4f}. "
                        f"Posterior mean: {top.get('posterior_mean',0):.4f}, "
                        f"Credible interval: [{top.get('credible_interval_lower',0):.4f}, {top.get('credible_interval_upper',0):.4f}].")
            lines.append(f"Based on {top.get('evidence_count',0)} observations.")
    if markov_results:
        hot_nums = [r for r in markov_results if r.get("current_state") == "hot"]
        cold_nums = [r for r in markov_results if r.get("current_state") == "cold"]
        if hot_nums: lines.append(f"{len(hot_nums)} numbers currently in HOT state (high frequency).")
        if cold_nums: lines.append(f"{len(cold_nums)} numbers currently in COLD state (low frequency).")
        if markov_results:
            avg_pers = sum(r.get("state_persistence",0) for r in markov_results) / len(markov_results)
            lines.append(f"Average state persistence: {avg_pers:.2f} (higher = more stable patterns).")
    lines.append("\n*Note: Probability analysis is for research purposes only. Does not predict future outcomes.*")
    return "\n".join(lines)


def compare_models(model_records: List[Dict[str, Any]]) -> str:
    """Compare multiple models and generate a comparison report."""
    if not model_records:
        return "No models to compare."
    lines = ["## Model Comparison", "", "| Model | Version | Type | Status | ROI | Sharpe | Drawdown |", "|-------|---------|------|--------|-----|--------|----------|"]
    for m in model_records:
        metrics = m.get("metrics", {})
        lines.append(f"| {m.get('model_id','?')} | {m.get('version','?')} | {m.get('model_type','?')} | "
                     f"{m.get('status','?')} | {metrics.get('roi','N/A')} | {metrics.get('sharpe_ratio','N/A')} | "
                     f"{metrics.get('max_drawdown_pct','N/A')} |")
    lines.append("")
    if len(model_records) > 1:
        best = max(model_records, key=lambda m: m.get("metrics",{}).get("sharpe_ratio", -999))
        lines.append(f"Best performing model: {best.get('model_id','?')} (Sharpe: {best.get('metrics',{}).get('sharpe_ratio','N/A')})")
    return "\n".join(lines)


def recommend_experiments(metrics: BacktestMetrics) -> List[Dict[str, Any]]:
    """Generate experiment recommendations based on backtest metrics."""
    recommendations = []
    if metrics.roi < 0:
        recommendations.append({"type":"parameter_optimization","priority":"high",
            "description":"ROI is negative. Run Grid Search to find better parameters.",
            "expected_impact":"positive"})
    if metrics.max_drawdown_pct > 20:
        recommendations.append({"type":"risk_management","priority":"high",
            "description":"Drawdown exceeds 20%. Consider adding stop-loss rules.",
            "expected_impact":"positive"})
    if metrics.sharpe_ratio < 0.5 and metrics.roi > 0:
        recommendations.append({"type":"risk_optimization","priority":"medium",
            "description":"Positive ROI but low Sharpe. Optimize for risk-adjusted returns.",
            "expected_impact":"positive"})
    if metrics.total_bets < 50:
        recommendations.append({"type":"data_collection","priority":"medium",
            "description":f"Only {metrics.total_bets} trades analyzed. Increase sample for robust conclusions.",
            "expected_impact":"neutral"})
    if not recommendations:
        recommendations.append({"type":"exploration","priority":"low",
            "description":"Current strategy performs well. Try A/B testing with different parameters.",
            "expected_impact":"positive"})
    return recommendations


def risk_assessment(metrics: BacktestMetrics) -> Dict[str, Any]:
    """Comprehensive risk assessment with warnings."""
    warnings = []
    if metrics.max_drawdown_pct > 25: warnings.append("CRITICAL: Extreme drawdown risk")
    elif metrics.max_drawdown_pct > 15: warnings.append("WARNING: Notable drawdown risk")
    if metrics.volatility > 2.0: warnings.append("WARNING: High volatility detected")
    if metrics.sharpe_ratio < -0.5: warnings.append("WARNING: Poor risk-adjusted returns")
    if metrics.max_consecutive_losses > 10: warnings.append("CRITICAL: Extended losing streak")
    return {"risk_level":"high" if any("CRITICAL" in w for w in warnings) else ("medium" if warnings else "low"),
            "warnings":warnings,"total_checks":5,"warnings_count":len(warnings)}
