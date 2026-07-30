"""Tests for StrategyAdvisor."""
from __future__ import annotations
import pytest
from engine.backtest.models import BacktestMetrics
from engine.intelligence.strategy_advisor import StrategyAdvisor
from engine.strategy.registry import StrategyDefinition

def _m(roi=5.0, wr=30.0, sharpe=0.5, dd=10.0, vol=1.0, bets=100, consec=5):
    return BacktestMetrics(total_investment=1000, total_return=1000+roi*10, roi=roi,
        win_count=int(wr*bets/100), total_bets=bets, win_rate=wr,
        max_drawdown_amount=dd*10, max_drawdown_pct=dd, volatility=vol,
        sharpe_ratio=sharpe, avg_return_per_bet=1.0, final_capital=1010.0,
        best_single_return=50.0, worst_single_return=-10.0,
        consecutive_losses=consec, max_consecutive_losses=consec)

def _t(win=False):
    from engine.backtest.models import TradeRecord
    return TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
        bet_main_numbers=[1,2,3,4,5], actual_main_numbers=[1,2,3,10,11],
        bet_amount=10.0, win_amount=20.0 if win else 0.0, is_win=win,
        prize_level=5 if win else 0, matched_main=3 if win else 0, matched_bonus=0,
        cumulative_pnl=10.0 if win else -10.0, cumulative_roi=1.0 if win else -1.0,
        bet_bonus_numbers=None, actual_bonus_numbers=None)

class TestStrategyAdvisor:
    def setup_method(self):
        self.advisor = StrategyAdvisor()

    def test_high_drawdown_high_priority(self):
        s = self.advisor.analyze(_m(dd=30.0), [_t()])
        assert any(x.priority == "high" and x.category == "risk_warning" for x in s)

    def test_medium_drawdown_medium_priority(self):
        s = self.advisor.analyze(_m(dd=18.0), [_t()])
        assert any(x.priority == "medium" for x in s)

    def test_high_volatility_warning(self):
        s = self.advisor.analyze(_m(vol=3.0), [_t()])
        assert any("volatility" in x.message for x in s)

    def test_long_losing_streak_warning(self):
        s = self.advisor.analyze(_m(consec=12), [_t()])
        assert any("consecutive" in x.message for x in s)

    def test_low_win_rate_negative_roi(self):
        s = self.advisor.analyze(_m(wr=5.0, roi=-20.0), [_t()])
        assert any("win rate" in x.message for x in s)

    def test_severe_loss_reduction(self):
        s = self.advisor.analyze(_m(roi=-40.0), [_t()])
        assert any("reduce" in x.message.lower() or "reduction" in x.message.lower() for x in s)

    def test_good_performance_low_priority(self):
        s = self.advisor.analyze(_m(roi=20.0, sharpe=1.5, dd=5.0), [_t()])
        assert all(x.priority != "high" for x in s)

    def test_suggestions_sorted_by_priority(self):
        s = self.advisor.analyze(_m(roi=-50.0, dd=35.0, sharpe=-1.0, vol=3.0, consec=15), [_t()])
        priorities = [x.priority for x in s]
        high_first = priorities.index("high") if "high" in priorities else len(priorities)
        med_first = priorities.index("medium") if "medium" in priorities else len(priorities)
        low_first = priorities.index("low") if "low" in priorities else len(priorities)
        assert high_first < med_first < low_first

    def test_suggest_weight_gap_based_negative(self):
        strat = StrategyDefinition({"strategy_id":"s", "name":"S", "strategy_type":"gap_based","params":{"min_gap":5}})
        s = self.advisor.suggest_weight_adjustments(strat, _m(roi=-30.0))
        assert len(s) > 0

    def test_suggest_weight_hot_negative(self):
        strat = StrategyDefinition({"strategy_id":"s", "name":"S", "strategy_type":"hot","params":{}})
        s = self.advisor.suggest_weight_adjustments(strat, _m(roi=-15.0))
        assert len(s) > 0

    def test_no_suggestions_default(self):
        s = self.advisor.analyze(_m(roi=5.0, wr=30.0, sharpe=0.3, dd=8.0), [_t()])
        assert len(s) > 0

    def test_cooldown_suggestion(self):
        s = self.advisor.analyze(_m(consec=9), [_t()])
        assert any("cooldown" in x.message.lower() or "pause" in x.message.lower() for x in s)

    def test_negative_sharpe_suggestion(self):
        s = self.advisor.analyze(_m(sharpe=-0.7, roi=-10.0), [_t()])
        assert any("sharpe" in x.message.lower() for x in s)
    def test_x_low_prize_detection(self):
        from engine.backtest.models import TradeRecord
        t = TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
            bet_main_numbers=[1,2,3,4,5], actual_main_numbers=[10,11,12,13,14],
            bet_amount=10.0, win_amount=5.0, is_win=True, prize_level=10,
            matched_main=0, matched_bonus=0, cumulative_pnl=-5.0, cumulative_roi=-0.5,
            bet_bonus_numbers=None, actual_bonus_numbers=None)
        m = _m(wr=20.0)
        m.total_investment = 100.0
        m.best_single_return = 5.0
        s = self.advisor.analyze(m, [t]*5)
        assert len(s) > 0
    def test_y_suggestion_has_category(self):
        s = self.advisor.analyze(_m(), [_t()])
        for x in s: assert hasattr(x, "category")
    def test_z_suggestion_has_priority(self):
        s = self.advisor.analyze(_m(), [_t()])
        for x in s: assert hasattr(x, "priority")
    def test_aa_suggestion_details_dict(self):
        s = self.advisor.analyze(_m(dd=30.0, vol=3.0), [_t()]*2)
        for x in s:
            if x.details: assert isinstance(x.details, dict)
    def test_ab_default_on_good_metrics(self):
        s = self.advisor.analyze(_m(roi=20.0, wr=50.0, sharpe=2.0, dd=5.0, vol=0.3), [_t()]*5)
        assert len(s) >= 1
    def test_ac_weight_adj_gap_based_positive(self):
        strat = StrategyDefinition({"strategy_id":"s","name":"S","strategy_type":"gap_based","params":{"min_gap":5}})
        s = self.advisor.suggest_weight_adjustments(strat, _m(roi=10.0, sharpe=0.8))
        assert len(s) >= 1
    def test_ad_weight_adj_no_issue(self):
        strat = StrategyDefinition({"strategy_id":"s","name":"S","strategy_type":"random","params":{}})
        s = self.advisor.suggest_weight_adjustments(strat, _m(roi=5.0))
        assert len(s) >= 1
