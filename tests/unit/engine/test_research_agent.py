"""Tests for ResearchAgent."""
from __future__ import annotations
import pytest
from engine.backtest.models import BacktestMetrics
from engine.intelligence.research_agent import ResearchAgent

def _m(roi=10.0, wr=30.0, sharpe=0.5, dd=15.0, vol=1.0, bets=100, consec=5):
    return BacktestMetrics(total_investment=1000, total_return=1000+roi*10, roi=roi,
        win_count=int(wr*bets/100), total_bets=bets, win_rate=wr,
        max_drawdown_amount=dd*10, max_drawdown_pct=dd, volatility=vol,
        sharpe_ratio=sharpe, avg_return_per_bet=1.0, final_capital=1010.0,
        best_single_return=50.0, worst_single_return=-10.0,
        consecutive_losses=consec, max_consecutive_losses=consec)

class TestResearchAgent:
    def setup_method(self):
        self.agent = ResearchAgent()

    def test_analyze_positive_roi(self):
        r = self.agent.analyze_backtest(_m(roi=15.0))
        assert r.key_metrics["roi"] == 15.0

    def test_analyze_negative_roi_warning(self):
        r = self.agent.analyze_backtest(_m(roi=-30.0))
        assert any(f.severity == "warning" for f in r.findings)

    def test_analyze_severe_loss_critical(self):
        r = self.agent.analyze_backtest(_m(roi=-60.0))
        assert any(f.severity == "critical" for f in r.findings)

    def test_low_win_rate_warning(self):
        r = self.agent.analyze_backtest(_m(wr=3.0))
        assert any("win rate" in f.message.lower() for f in r.findings)

    def test_high_sharpe_info(self):
        r = self.agent.analyze_backtest(_m(sharpe=1.5))
        assert any(f.severity == "info" and "sharpe" in f.message.lower() for f in r.findings)

    def test_high_drawdown_critical(self):
        r = self.agent.analyze_backtest(_m(dd=40.0))
        assert any(f.severity == "critical" and "drawdown" in f.message.lower() for f in r.findings)

    def test_low_drawdown_info(self):
        r = self.agent.analyze_backtest(_m(dd=5.0))
        assert any(f.severity == "info" and "drawdown" in f.message.lower() for f in r.findings)

    def test_long_losing_streak_critical(self):
        r = self.agent.analyze_backtest(_m(consec=15))
        assert any(f.severity == "critical" for f in r.findings)

    def test_risk_score_low(self):
        r = self.agent.analyze_backtest(_m(roi=20.0, dd=5.0, sharpe=1.5))
        assert r.risk_assessment["risk_score"] < 0.5

    def test_risk_score_high(self):
        r = self.agent.analyze_backtest(_m(roi=-50.0, dd=40.0, sharpe=-1.0))
        assert r.risk_assessment["risk_score"] > 0.5

    def test_confidence_low_on_few_bets(self):
        r = self.agent.analyze_backtest(_m(bets=5))
        assert r.confidence_score < 0.5

    def test_confidence_high_on_many_bets(self):
        r = self.agent.analyze_backtest(_m(bets=300))
        assert r.confidence_score > 0.7

    def test_summary_contains_roi(self):
        r = self.agent.analyze_backtest(_m(roi=25.0))
        assert "25" in r.summary

    def test_improvement_suggestions_present(self):
        r = self.agent.analyze_backtest(_m(roi=-10.0, sharpe=-0.3))
        assert len(r.improvement_suggestions) > 0

    def test_compare_strategies_ranking(self):
        results = [
            {"strategy_id": "a", "name": "A", "metrics": _m(sharpe=0.8)},
            {"strategy_id": "b", "name": "B", "metrics": _m(sharpe=0.2)},
        ]
        c = self.agent.compare_strategies(results)
        assert c["strategies_compared"] == 2
        assert c["ranking"][0]["strategy_id"] == "a"

    def test_compare_no_strategies(self):
        c = self.agent.compare_strategies([])
        assert c["strategies_compared"] == 0

    def test_volatility_warning(self):
        r = self.agent.analyze_backtest(_m(vol=3.0))
        assert any("volatility" in f.message.lower() for f in r.findings)

    def test_risk_level_low(self):
        r = self.agent.analyze_backtest(_m(roi=20.0, dd=5.0, sharpe=2.0, vol=0.5))
        assert r.risk_assessment["risk_level"] == "low"

    def test_risk_level_high(self):
        r = self.agent.analyze_backtest(_m(roi=-50.0, dd=40.0, sharpe=-1.5, vol=3.0))
        assert r.risk_assessment["risk_level"] == "high"
    def test_0_roi_improvement_suggestion(self):
        r = self.agent.analyze_backtest(_m(roi=-5.0)); assert len(r.improvement_suggestions) > 0
    def test_1_high_sharpe_no_critical(self):
        r = self.agent.analyze_backtest(_m(sharpe=2.0, roi=15.0)); assert not any(f.severity=="critical" for f in r.findings)
    def test_2_comparison_single_strategy(self):
        c = self.agent.compare_strategies([{"strategy_id":"a","name":"A","metrics":_m()}])
        assert c["strategies_compared"] == 1
    def test_3_risk_level_medium(self):
        r = self.agent.analyze_backtest(_m(roi=-5.0, dd=18.0, sharpe=-0.2)); assert r.risk_assessment["risk_level"] in ["medium","high"]
    def test_4_empty_findings_on_good_perf(self):
        r = self.agent.analyze_backtest(_m(roi=20.0, wr=50.0, sharpe=1.5, dd=5.0, vol=0.5))
        assert not any(f.severity=="critical" for f in r.findings)
    def test_5_critical_counted(self):
        r = self.agent.analyze_backtest(_m(roi=-60.0, dd=40.0)); assert any(f.severity=="critical" for f in r.findings)
