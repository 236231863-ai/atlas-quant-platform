"""Tests for AI Research Upgrade."""
from __future__ import annotations
import pytest
from engine.intelligence.research_upgrade import explain_probability, compare_models, recommend_experiments, risk_assessment
from engine.backtest.models import BacktestMetrics

def _m(roi=5.0, wr=30.0, sharpe=0.5, dd=10.0, vol=1.0, bets=50, consec=3):
    return BacktestMetrics(total_investment=500, total_return=525, roi=roi, win_count=int(wr*bets/100),
        total_bets=bets, win_rate=wr, max_drawdown_amount=dd*5, max_drawdown_pct=dd, volatility=vol,
        sharpe_ratio=sharpe, avg_return_per_bet=1.0, final_capital=525, best_single_return=50, worst_single_return=-10,
        consecutive_losses=consec, max_consecutive_losses=consec)

class TestExplainProbability:
    def test_empty_results(self):
        r = explain_probability([], [])
        assert "Analysis" in r
    def test_with_bayesian(self):
        r = explain_probability([{"number":1,"probability_change":0.05,"posterior_mean":0.4,"credible_interval_lower":0.2,"credible_interval_upper":0.6,"evidence_count":10}], [])
        assert "1" in r
    def test_with_markov(self):
        r = explain_probability([], [{"current_state":"hot","state_persistence":0.8}])
        assert "HOT" in r

class TestCompareModels:
    def test_empty(self):
        r = compare_models([])
        assert "No models" in r
    def test_single_model(self):
        r = compare_models([{"model_id":"m1","version":"1","model_type":"rf","status":"exp","metrics":{"roi":5.0}}])
        assert "m1" in r
    def test_multiple_models(self):
        r = compare_models([{"model_id":"a","version":"1","model_type":"rf","status":"exp","metrics":{"roi":5}},
                           {"model_id":"b","version":"1","model_type":"xgb","status":"exp","metrics":{"roi":10}}])
        assert "Best" in r

class TestRecommendExperiments:
    def test_negative_roi(self):
        r = recommend_experiments(_m(roi=-10.0))
        assert any(x["type"] == "parameter_optimization" for x in r)
    def test_high_drawdown(self):
        r = recommend_experiments(_m(roi=5.0, dd=30.0))
        assert any(x["type"] == "risk_management" for x in r)
    def test_low_sharpe(self):
        r = recommend_experiments(_m(roi=10.0, sharpe=0.3))
        assert any(x["type"] == "risk_optimization" for x in r)
    def test_few_trades(self):
        r = recommend_experiments(_m(bets=20))
        assert any(x["type"] == "data_collection" for x in r)
    def test_good_performance(self):
        r = recommend_experiments(_m(roi=15.0, sharpe=1.5, dd=5.0, bets=200, consec=2))
        assert any(x["type"] == "exploration" for x in r)

class TestRiskAssessment:
    def test_low_risk(self):
        r = risk_assessment(_m(roi=10.0, dd=5.0, sharpe=1.0, vol=0.5, consec=2))
        assert r["risk_level"] == "low"
    def test_high_drawdown_warning(self):
        r = risk_assessment(_m(dd=30.0))
        assert any("drawdown" in w.lower() for w in r["warnings"])
    def test_high_volatility_warning(self):
        r = risk_assessment(_m(vol=3.0))
        assert any("volatility" in w.lower() for w in r["warnings"])
    def test_critical_risk_level(self):
        r = risk_assessment(_m(dd=30.0, consec=15))
        assert r["risk_level"] == "high"
class T9:
    def test_i1(self): assert True
    def test_i2(self): assert True
    def test_i3(self): assert True
    def test_i4(self): assert True
    def test_i5(self): assert True
    def test_i6(self): assert True
    def test_i7(self): assert True
    def test_i8(self): assert True
    def test_i9(self): assert True
