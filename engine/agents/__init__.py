"""Multi-Agent Research System."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.backtest.models import BacktestMetrics
from engine.intelligence.research_upgrade import risk_assessment

@dataclass
class AgentReport:
    agent: str; analysis: str; recommendations: List[str]; confidence: float = 0.5
    def to_dict(self):
        return asdict(self)

class StatisticianAgent:
    def analyze(self, metrics: BacktestMetrics, history: List[Dict[str, Any]]) -> AgentReport:
        lines = [f"Analyzed {metrics.total_bets} bets.", f"ROI: {metrics.roi:.2f}%, Win Rate: {metrics.win_rate:.1f}%"]
        recs = []
        if metrics.roi < 0: recs.append("Strategy is losing capital - review parameters")
        if metrics.win_rate < 10: recs.append("Very low win rate - consider different approach")
        if metrics.sharpe_ratio < 0: recs.append("Negative risk-adjusted returns")
        if not recs: recs.append("Statistics within normal range")
        return AgentReport(agent="Statistician", analysis=" ".join(lines), recommendations=recs)

class OptimizationAgent:
    def analyze(self, metrics: BacktestMetrics) -> AgentReport:
        recs = []
        if metrics.roi < 0: recs.append("Run Bayesian optimization on strategy parameters")
        if metrics.sharpe_ratio < 0.5: recs.append("Optimize for Sharpe ratio")
        if metrics.max_drawdown_pct > 20: recs.append("Add drawdown constraints to optimization")
        if not recs: recs.append("Current parameters appear optimal")
        return AgentReport(agent="Optimizer", analysis=f"Sharpe: {metrics.sharpe_ratio:.2f}, ROI: {metrics.roi:.1f}%", recommendations=recs)

class RiskAgent:
    def analyze(self, metrics: BacktestMetrics) -> AgentReport:
        r = risk_assessment(metrics)
        return AgentReport(agent="Risk", analysis=f"Risk level: {r['risk_level']}, {len(r['warnings'])} warnings",
                          recommendations=r["warnings"] if r["warnings"] else ["Risk within acceptable bounds"],
                          confidence=0.4 if r["risk_level"] == "high" else 0.8)

class ReviewerAgent:
    def review(self, reports: List[AgentReport]) -> AgentReport:
        total_recs = sum(len(r.recommendations) for r in reports)
        high_confidence = sum(1 for r in reports if r.confidence > 0.6)
        concerns = [r for r in reports if r.confidence < 0.4]
        lines = [f"Reviewed {len(reports)} agent reports.", f"Total recommendations: {total_recs}."]
        recs = []
        if concerns: recs.append(f"{len(concerns)} agents have low confidence - review their analyses")
        if not recs: recs.append("All agents report consistent findings")
        return AgentReport(agent="Reviewer", analysis=" ".join(lines), recommendations=recs, confidence=0.7)

class CoordinatorAgent:
    def __init__(self):
        self._stat = StatisticianAgent()
        self._opt = OptimizationAgent()
        self._risk = RiskAgent(); self._review = ReviewerAgent()

    def run_research(self, metrics: BacktestMetrics, history: List[Dict[str, Any]]) -> AgentReport:
        r1 = self._stat.analyze(metrics, history)
        r2 = self._opt.analyze(metrics)
        r3 = self._risk.analyze(metrics)
        r4 = self._review.review([r1, r2, r3])
        all_recs = r1.recommendations + r2.recommendations + r3.recommendations + r4.recommendations
        lines = [f"Coordinated {len([r1,r2,r3,r4])} agents.",
                 f"Statistician: {r1.analysis}", f"Optimizer: {r2.analysis}",
                 f"Risk: {r3.analysis}", f"Review: {r4.analysis}"]
        return AgentReport(agent="Coordinator", analysis="\n".join(lines),
                          recommendations=all_recs[:5], confidence=0.6)
