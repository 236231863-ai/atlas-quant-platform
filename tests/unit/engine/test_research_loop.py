"""Tests for Automated Research Loop."""
from __future__ import annotations
import pytest
from engine.research import ResearchLoopEngine, ResearchCycleReport
from engine.backtest.models import BacktestMetrics

def _m(roi=5.0, sharpe=0.5, dd=10.0, wr=30.0, bets=100, consec=3):
    return BacktestMetrics(total_investment=500,total_return=525,roi=roi,win_count=int(wr*bets/100),
        total_bets=bets,win_rate=wr,max_drawdown_amount=dd*5,max_drawdown_pct=dd,volatility=1.0,
        sharpe_ratio=sharpe,avg_return_per_bet=1.0,final_capital=525,best_single_return=50,
        worst_single_return=-10,consecutive_losses=consec,max_consecutive_losses=consec)

class TestResearchLoop:
    def setup_method(self): self.engine = ResearchLoopEngine()
    def test_generate_hypothesis_empty(self):
        h = self.engine.generate_hypothesis([])
        assert "baseline" in h.lower() or "random" in h.lower()
    def test_generate_from_history(self):
        h = self.engine.generate_hypothesis([{"metrics":{"sharpe_ratio":0.3,"roi":5.0}}])
        assert "adjust" in h.lower() or "improve" in h.lower() or "replace" in h.lower()
    def test_create_experiment(self):
        e = self.engine.create_experiment("Test hypothesis", {"x":[1,2]})
        assert e["status"] == "ready"
    def test_cycle_count_increments(self):
        self.engine.create_experiment("H1", {"x":[1]}); self.engine.create_experiment("H2", {"x":[1]})
        assert self.engine._cycle_count == 2
    def test_evaluate_metrics(self):
        ev = self.engine.evaluate_metrics(_m(roi=10.0, sharpe=0.8))
        assert ev["roi"] == 10.0; assert ev["sharpe"] == 0.8
    def test_analyze_failure_severe(self):
        f = self.engine.analyze_failure(_m(roi=-40.0, dd=30.0), "Hyp")
        assert "loss" in f
    def test_analyze_failure_general(self):
        f = self.engine.analyze_failure(_m(roi=-5.0), "Hyp")
        assert "improvement" in f
    def test_recommend_next_negative_roi(self):
        r = self.engine.recommend_next(_m(roi=-10.0))
        assert any("strategy" in x.lower() for x in r)
    def test_recommend_next_high_dd(self):
        r = self.engine.recommend_next(_m(roi=5.0, dd=25.0))
        assert any("drawdown" in x.lower() for x in r)
    def test_recommend_next_default(self):
        r = self.engine.recommend_next(_m(roi=10.0, sharpe=1.5, dd=5.0, bets=200))
        assert any("optimal" in x.lower() or "viable" in x.lower() for x in r)
    def test_full_cycle(self):
        r = self.engine.execute_cycle([], _m(roi=-10.0), {"x":[1,2]})
        assert isinstance(r, ResearchCycleReport)
    def test_full_cycle_has_recs(self):
        r = self.engine.execute_cycle([{"metrics":{"roi":5,"sharpe":0.3}}], _m(roi=-10.0), {"x":[1,2]})
        assert len(r.recommendations) > 0
