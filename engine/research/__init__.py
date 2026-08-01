"""Automated Research Loop Engine."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.backtest.models import BacktestMetrics

@dataclass
class ResearchCycleReport:
    hypothesis: str; experiment_config: Dict[str, Any]; result_summary: Dict[str, Any]
    recommendations: List[str]; cycle_id: str = "cycle_1"
    def to_dict(self):
        return asdict(self)

class ResearchLoopEngine:
    def __init__(self):
        self._cycle_count = 0

    def generate_hypothesis(self, experiment_history: List[Dict[str, Any]]) -> str:
        if not experiment_history: return "Test baseline random strategy performance"
        last = experiment_history[-1]
        metrics = last.get("metrics", {})
        if metrics.get("sharpe_ratio", 0) < 0.5 and metrics.get("roi", 0) > 0:
            return f"Improve risk-adjusted returns by adjusting weights"
        elif metrics.get("roi", 0) < 0:
            return f"Replace underperforming parameters with gap-based approach"
        else:
            return f"Explore parameter space around current best: {last.get('params', {})}"

    def create_experiment(self, hypothesis: str, param_space: Dict[str, List[Any]]) -> Dict[str, Any]:
        self._cycle_count += 1
        return {"cycle": self._cycle_count, "hypothesis": hypothesis,
                "param_space": param_space, "status": "ready"}

    def evaluate_metrics(self, metrics: BacktestMetrics) -> Dict[str, Any]:
        return {"roi": round(metrics.roi, 2), "sharpe": round(metrics.sharpe_ratio, 4),
                "max_dd": round(metrics.max_drawdown_pct, 2), "win_rate": round(metrics.win_rate, 2),
                "total_bets": metrics.total_bets}

    def analyze_failure(self, metrics: BacktestMetrics, hypothesis: str) -> str:
        reasons = []
        if metrics.roi < -30: reasons.append("Severe capital loss")
        if metrics.max_drawdown_pct > 25: reasons.append("High drawdown")
        if metrics.sharpe_ratio < -0.5: reasons.append("Poor risk-adjusted returns")
        if metrics.max_consecutive_losses > 10: reasons.append("Extended losing streak")
        if not reasons: reasons.append("Hypothesis did not produce expected improvement")
        return f"Hypothesis failed: {', '.join(reasons)}"

    def recommend_next(self, metrics: BacktestMetrics) -> List[str]:
        recs = []
        if metrics.roi < 0: recs.append("Try different strategy type")
        if metrics.max_drawdown_pct > 20: recs.append("Add drawdown limit")
        if metrics.sharpe_ratio < 0.3: recs.append("Optimize for Sharpe, not ROI")
        if metrics.total_bets < 30: recs.append("Increase sample size")
        if not recs: recs.append("Current approach viable, continue optimization")
        return recs

    def execute_cycle(self, history: List[Dict[str, Any]], metrics: BacktestMetrics,
                      param_space: Dict[str, List[Any]]) -> ResearchCycleReport:
        hypothesis = self.generate_hypothesis(history)
        experiment = self.create_experiment(hypothesis, param_space)
        evaluation = self.evaluate_metrics(metrics)
        failure = self.analyze_failure(metrics, hypothesis) if metrics.roi < 0 else ""
        recs = self.recommend_next(metrics)
        return ResearchCycleReport(hypothesis=hypothesis, experiment_config=experiment,
            result_summary={"evaluation": evaluation, "failure_analysis": failure} if failure else {"evaluation": evaluation},
            recommendations=recs)
