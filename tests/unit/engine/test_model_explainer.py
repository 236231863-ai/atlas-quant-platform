"""Tests for ModelExplainer."""
from __future__ import annotations
import pytest
from engine.backtest.models import BacktestMetrics, TradeRecord
from engine.intelligence.model_explainer import ModelExplainer

def _t(win=False, amt=0.0, pl=0):
    return TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
        bet_main_numbers=[1,2,3,4,5], actual_main_numbers=[1,2,3,10,11],
        bet_amount=10.0, win_amount=amt, is_win=win, prize_level=pl,
        matched_main=3 if win else 0, matched_bonus=0,
        cumulative_pnl=0.0, cumulative_roi=0.0,
        bet_bonus_numbers=None, actual_bonus_numbers=None)

def _m(roi=5.0, wr=20.0, sharpe=0.3, dd=10.0, vol=0.8, bets=50):
    return BacktestMetrics(total_investment=500, total_return=525, roi=roi,
        win_count=int(wr*bets/100), total_bets=bets, win_rate=wr,
        max_drawdown_amount=dd*5, max_drawdown_pct=dd, volatility=vol,
        sharpe_ratio=sharpe, avg_return_per_bet=0.5, final_capital=525.0,
        best_single_return=30.0, worst_single_return=-10.0,
        consecutive_losses=3, max_consecutive_losses=3)

class TestModelExplainer:
    def setup_method(self):
        self.explainer = ModelExplainer()

    def test_empty_trades(self):
        r = self.explainer.analyze_performance(_m(), [])
        assert "No trades" in r["explanation"]

    def test_win_trades_counted(self):
        trades = [_t(win=True, amt=20.0, pl=5)] * 10 + [_t()] * 10
        r = self.explainer.analyze_performance(_m(wr=50.0), trades)
        assert r["overall"]["win_trades"] == 10

    def test_avg_win_amount(self):
        trades = [_t(win=True, amt=50.0, pl=3)] * 5
        r = self.explainer.analyze_performance(_m(), trades)
        assert r["overall"]["avg_win_amount"] == 50.0

    def test_prize_contributions(self):
        trades = [_t(win=True, amt=100.0, pl=1)] * 2 + [_t(win=True, amt=10.0, pl=5)] * 3
        m = _m(roi=20.0)
        m.total_return = 230.0
        r = self.explainer.analyze_performance(m, trades)
        assert len(r["win_contributions"]) > 0

    def test_feature_importance_returns_list(self):
        r = self.explainer.compute_feature_importance([_t(), _t(win=True, amt=20.0, pl=3)], _m())
        assert len(r) > 0

    def test_feature_importance_sorted(self):
        r = self.explainer.compute_feature_importance([_t(win=True, amt=50.0, pl=2)]*5, _m(wr=50.0))
        for i in range(len(r)-1):
            assert r[i].importance_score >= r[i+1].importance_score

    def test_feature_importance_empty_trades(self):
        r = self.explainer.compute_feature_importance([], _m())
        assert r == []

    def test_explanation_positive_roi(self):
        r = self.explainer.generate_explanation(_m(roi=20.0), [])
        assert "positive" in r

    def test_explanation_negative_roi(self):
        r = self.explainer.generate_explanation(_m(roi=-20.0), [])
        assert "negative" in r

    def test_explanation_includes_top_factor(self):
        imp = [self.explainer.FeatureImportance("test", 0.9, "positive", "test feature")]
        r = self.explainer.generate_explanation(_m(), imp)
        assert "test" in r

    def test_performance_factors_present(self):
        trades = [_t(win=True, amt=20.0, pl=5)] * 5 + [_t()] * 5
        r = self.explainer.analyze_performance(_m(wr=50.0), trades)
        assert len(r["performance_factors"]) == 4

    def test_risk_reward_factor(self):
        trades = [_t(win=True, amt=30.0, pl=5)] * 5 + [_t()] * 5
        r = self.explainer.analyze_performance(_m(wr=50.0), trades)
        factors = {f["factor"]: f for f in r["performance_factors"]}
        assert "risk_reward_ratio" in factors
    def test_a_avg_loss_amt(self):
        t = [_t(win=True, amt=30.0, pl=3)]*3+[_t()]*7
        r = self.explainer.analyze_performance(_m(wr=30.0), t)
        assert r["overall"]["loss_trades"] == 7
    def test_b_profit_factor(self):
        r = self.explainer.analyze_performance(_m(), [_t()])
        assert r["overall"]["profit_factor"] >= 0
    def test_c_feature_importance_dd_negative(self):
        r = self.explainer.compute_feature_importance([_t()], _m(dd=35.0))
        d = [f for f in r if f.feature_name=="drawdown_control"]
        assert len(d) > 0 and d[0].direction == "negative"
    def test_d_feature_importance_wr_positive(self):
        r = self.explainer.compute_feature_importance([_t(win=True, amt=10, pl=5)], _m(wr=40.0))
        w = [f for f in r if f.feature_name=="win_frequency"]
        assert len(w) > 0 and w[0].direction == "positive"
    def test_e_explanation_has_bet_count(self):
        r = self.explainer.generate_explanation(_m(bets=200), [])
        assert "200" in r
    def test_f_consistency_factor(self):
        r = self.explainer.analyze_performance(_m(vol=0.3), [_t()]*10)
        factors = {f["factor"]:f for f in r["performance_factors"]}
        assert factors["consistency"]["impact"] == "stable"
    def test_g_volatility_impact_high(self):
        r = self.explainer.analyze_performance(_m(vol=3.0), [_t()]*10)
        factors = {f["factor"]:f for f in r["performance_factors"]}
        assert "high_risk" in factors["consistency"]["impact"]
    def test_h_drawdown_severity_severe(self):
        r = self.explainer.analyze_performance(_m(dd=35.0), [_t()]*10)
        factors = {f["factor"]:f for f in r["performance_factors"]}
        assert factors["drawdown_severity"]["interpretation"] == "Severe"
