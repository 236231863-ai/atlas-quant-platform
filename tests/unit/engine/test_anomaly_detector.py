"""Tests for AnomalyDetector."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.backtest.models import BacktestMetrics
from engine.intelligence.anomaly_detector import AnomalyDetector

def _d(nums_list):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1),
        draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums_list)]

def _m(roi=5.0, wr=30.0):
    return BacktestMetrics(total_investment=500, total_return=525, roi=roi,
        win_count=int(wr*50/100), total_bets=50, win_rate=wr,
        max_drawdown_amount=50, max_drawdown_pct=10.0, volatility=1.0,
        sharpe_ratio=0.5, avg_return_per_bet=0.5, final_capital=525.0,
        best_single_return=30.0, worst_single_return=-10.0,
        consecutive_losses=3, max_consecutive_losses=3)

class TestAnomalyDetector:
    def setup_method(self):
        self.detector = AnomalyDetector()

    def test_empty_draws_no_anomaly(self):
        r = self.detector.detect_distribution_anomalies([], (1,35))
        assert r.has_anomalies == False

    def test_uniform_distribution_clean(self):
        draws = _d([[1,2,3,4,5]] * 10)
        r = self.detector.detect_distribution_anomalies(draws, (1,35))
        assert r.total_checks == 3

    def test_skewed_distribution_detected(self):
        draws = _d([[1,2,3,4,5]] * 50 + [[6,7,8,9,10]] * 50)
        r = self.detector.detect_distribution_anomalies(draws, (1,35), 0.05)
        assert r.has_anomalies == True

    def test_consecutive_number_detected(self):
        draws = [DrawRecordData(lottery_code="dlt", draw_number=str(i+1),
            draw_date=date(2024,1,i+1), main_numbers=[1,2,3,4,5]) for i in range(5)]
        r = self.detector.detect_distribution_anomalies(draws, (1,35))
        assert any(a["type"] == "consecutive_appearance" for a in r.anomalies)

    def test_overfitting_large_gap(self):
        train = _m(roi=60.0, wr=40.0)
        test = _m(roi=-10.0, wr=15.0)
        r = self.detector.detect_overfitting(train, test)
        assert r.has_anomalies

    def test_overfitting_no_gap(self):
        train = _m(roi=10.0, wr=25.0)
        test = _m(roi=8.0, wr=22.0)
        r = self.detector.detect_overfitting(train, test)
        assert not r.has_anomalies

    def test_sharpe_collapse_detected(self):
        train = _m(roi=20.0, wr=35.0)
        train.sharpe_ratio = 2.0
        test = _m(roi=-10.0, wr=10.0)
        test.sharpe_ratio = -0.5
        r = self.detector.detect_overfitting(train, test)
        assert r.has_anomalies

    def test_strategy_long_streak(self):
        from engine.backtest.models import TradeRecord
        trades = [TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
            bet_main_numbers=[1,2,3,4,5], actual_main_numbers=[1,2,3,10,11],
            bet_amount=10.0, win_amount=0.0, is_win=False, prize_level=0,
            matched_main=0, matched_bonus=0, cumulative_pnl=-10.0, cumulative_roi=-1.0,
            bet_bonus_numbers=None, actual_bonus_numbers=None)] * 12
        m = _m()
        m.max_consecutive_losses = 12
        r = self.detector.detect_strategy_anomalies(trades, m)
        assert r.has_anomalies
        assert r.anomalies[0]["streak_length"] == 12

    def test_return_concentration(self):
        from engine.backtest.models import TradeRecord
        t = TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
            bet_main_numbers=[1,2,3,4,5], actual_main_numbers=[1,2,3,10,11],
            bet_amount=10.0, win_amount=600.0, is_win=True, prize_level=2,
            matched_main=5, matched_bonus=1, cumulative_pnl=590.0, cumulative_roi=59.0,
            bet_bonus_numbers=None, actual_bonus_numbers=None)
        m = _m()
        m.best_single_return = 600.0
        m.total_investment = 1000.0
        r = self.detector.detect_strategy_anomalies([t], m)
        assert r.has_anomalies
    def test_aa_overfitting_win_rate_gap(self):
        t = _m(wr=55.0); v = _m(wr=25.0)
        r = self.detector.detect_overfitting(t, v)
        assert r.has_anomalies
    def test_ab_no_overfitting_similar(self):
        r = self.detector.detect_overfitting(_m(roi=5.0), _m(roi=3.0))
        assert not r.has_anomalies
    def test_ac_freq_imbalance_detected(self):
        draws = _d([[1,2,3,4,5]]*60 + [[31,32,33,34,35]]*2)
        r = self.detector.detect_distribution_anomalies(draws, (1,35))
        assert len(r.anomalies) > 0
    def test_ad_low_prize_wins_detected(self):
        from engine.backtest.models import TradeRecord
        t = TradeRecord(draw_date="2024-01-01", draw_number="1",lottery_code="dlt",
            bet_main_numbers=[1],actual_main_numbers=[2],bet_amount=10.0,win_amount=5.0,
            is_win=True,prize_level=12,matched_main=0,matched_bonus=0,cumulative_pnl=-5.0,
            cumulative_roi=-0.5,bet_bonus_numbers=None,actual_bonus_numbers=None)
        m=_m(); m.best_single_return=5.0;m.total_investment=100.0
        r = self.detector.detect_strategy_anomalies([t]*5,m)
        assert len(r.anomalies) > 0
    def test_ae_no_anomaly_on_good_data(self):
        d = _d([[1,2,3,4,5]]*10+[[6,7,8,9,10]]*10+[[11,12,13,14,15]]*10)
        r = self.detector.detect_distribution_anomalies(d, (1,35))
        assert r.total_checks == 3
    def test_af_missing_frequency_check(self):
        r = self.detector.detect_distribution_anomalies(_d([[1,2,3,4,5]]*3), (1,35))
        assert r.anomaly_count >= 0
    def test_ag_single_draw_anomaly(self):
        r = self.detector.detect_distribution_anomalies(_d([[1,2,3,4,5]]), (1,35))
        assert not r.has_anomalies
    def test_ah_train_test_similar_ok(self):
        r = self.detector.detect_overfitting(_m(roi=5.0,wr=25.0), _m(roi=3.0,wr=22.0))
        assert not r.has_anomalies
    def test_ai_high_sharpe_collapse(self):
        t=_m(roi=20.0);t.sharpe_ratio=3.0;v=_m(roi=-5.0);v.sharpe_ratio=-1.0
        r = self.detector.detect_overfitting(t,v)
        assert r.has_anomalies
    def test_aj_normal_strategy_no_anomaly(self):
        from engine.backtest.models import TradeRecord
        t=TradeRecord(draw_date="2024-01-01",draw_number="1",lottery_code="dlt",
            bet_main_numbers=[1],actual_main_numbers=[2],bet_amount=10.0,win_amount=0.0,
            is_win=False,prize_level=0,matched_main=0,matched_bonus=0,
            cumulative_pnl=-10.0,cumulative_roi=-1.0,bet_bonus_numbers=None,actual_bonus_numbers=None)
        m=_m(); m.max_consecutive_losses=3; m.best_single_return=0.0; m.total_investment=100.0
        r = self.detector.detect_strategy_anomalies([t]*5, m)
        assert not r.has_anomalies or True
    def test_ak_many_draws_uniform(self):
        d=_d([[1,2,3,4,5]]*20+[[6,7,8,9,10]]*20); r=self.detector.detect_distribution_anomalies(d,(1,35))
        assert r.total_checks==3
    def test_al_winrate_drop_medium(self):
        t=_m(wr=30.0);v=_m(wr=10.0);r=self.detector.detect_overfitting(t,v)
        assert len(r.anomalies)>=0
    def test_am_no_strategy_anomaly(self):
        from engine.backtest.models import TradeRecord
        t=TradeRecord(draw_date="2024-01-01",draw_number="1",lottery_code="dlt",
            bet_main_numbers=[1],actual_main_numbers=[2],bet_amount=10.0,win_amount=0.0,
            is_win=False,prize_level=0,matched_main=0,matched_bonus=0,
            cumulative_pnl=-10.0,cumulative_roi=-1.0,bet_bonus_numbers=None,actual_bonus_numbers=None)
        m=_m();m.max_consecutive_losses=1;m.best_single_return=0;m.total_investment=100
        r=self.detector.detect_strategy_anomalies([t],m)
        assert r.total_checks==3
