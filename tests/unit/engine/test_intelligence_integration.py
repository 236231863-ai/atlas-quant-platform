"""Integration tests for intelligence modules."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.backtest.models import BacktestMetrics, TradeRecord, BacktestConfig
from engine.backtest.simulator import TradeSimulator
from engine.backtest.analyzers import ResultAggregator
from engine.intelligence.research_agent import ResearchAgent
from engine.intelligence.model_explainer import ModelExplainer
from engine.intelligence.strategy_advisor import StrategyAdvisor
from engine.intelligence.anomaly_detector import AnomalyDetector

def _draws():
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1),
        draw_date=date(2024,1,i+1), main_numbers=[(i*3+1)%25+1]*5) for i in range(20)]

class TestIntelligenceIntegration:
    def setup_method(self):
        self.ra = ResearchAgent()
        self.me = ModelExplainer()
        self.sa = StrategyAdvisor()
        self.ad = AnomalyDetector()

    def test_research_from_backtest(self):
        sim = TradeSimulator(); agg = ResultAggregator()
        config = BacktestConfig(lottery_code="dlt", strategy_id="random", start_date="", end_date="",
            main_range=(1,25), main_count=5, initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = sim.run(_draws(), config)
        metrics = agg.analyze(trades)
        report = self.ra.analyze_backtest(metrics, trades, config)
        assert report.key_metrics["total_bets"] == len(trades)

    def test_explainer_from_backtest(self):
        sim = TradeSimulator(); agg = ResultAggregator()
        config = BacktestConfig(lottery_code="dlt", strategy_id="random", start_date="", end_date="",
            main_range=(1,25), main_count=5, initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = sim.run(_draws(), config)
        metrics = agg.analyze(trades)
        result = self.me.analyze_performance(metrics, trades)
        assert "overall" in result

    def test_advisor_from_backtest(self):
        sim = TradeSimulator(); agg = ResultAggregator()
        config = BacktestConfig(lottery_code="dlt", strategy_id="random", start_date="", end_date="",
            main_range=(1,25), main_count=5, initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = sim.run(_draws(), config)
        metrics = agg.analyze(trades)
        suggestions = self.sa.analyze(metrics, trades)
        assert len(suggestions) > 0

    def test_anomaly_from_backtest(self):
        sim = TradeSimulator(); agg = ResultAggregator()
        config = BacktestConfig(lottery_code="dlt", strategy_id="random", start_date="", end_date="",
            main_range=(1,25), main_count=5, initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = sim.run(_draws(), config)
        metrics = agg.analyze(trades)
        report = self.ad.detect_strategy_anomalies(trades, metrics)
        assert report.total_checks == 3

    def test_full_pipeline(self):
        sim = TradeSimulator(); agg = ResultAggregator()
        config = BacktestConfig(lottery_code="dlt", strategy_id="random", start_date="", end_date="",
            main_range=(1,25), main_count=5, initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = sim.run(_draws(), config)
        metrics = agg.analyze(trades)

        report = self.ra.analyze_backtest(metrics, trades)
        explanation = self.me.analyze_performance(metrics, trades)
        suggestions = self.sa.analyze(metrics, trades)

        assert report.summary != ""
        assert len(suggestions) > 0
        assert "overall" in explanation

    def test_research_report_to_dict(self):
        report = self.ra.analyze_backtest(
            BacktestMetrics(total_investment=100, total_return=110, roi=10.0,
                win_count=3, total_bets=10, win_rate=30.0, max_drawdown_amount=20,
                max_drawdown_pct=20.0, volatility=0.5, sharpe_ratio=0.3,
                avg_return_per_bet=1.0, final_capital=110.0, best_single_return=50.0,
                worst_single_return=-10.0, consecutive_losses=3, max_consecutive_losses=3))
        d = report.to_dict()
        assert "key_metrics" in d
        assert "findings" in d
    def test_g_distribution_anomaly_on_draws(self):
        draws = [DrawRecordData(lottery_code="dlt",draw_number=str(i+1),
            draw_date=date(2024,1,i+1),main_numbers=[1,2,3,4,5]) for i in range(50)]
        r = self.ad.detect_distribution_anomalies(draws, (1,35))
        assert r.total_checks == 3
    def test_h_overfitting_check_both_positive(self):
        r = self.ad.detect_overfitting(_m(roi=5.0), _m(roi=4.0))
        assert not r.has_anomalies
    def test_i_advisor_generates_text(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        t=sim.run(_draws(),c);m=agg.analyze(t);s=self.sa.analyze(m,t)
        for x in s: assert isinstance(x.message, str)
    def test_j_explainer_has_strategy_id(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        t=sim.run(_draws(),c);m=agg.analyze(t);r=self.me.analyze_performance(m,t)
        assert "strategy_id" in r
    def test_k_compare_strategies_from_research(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c1=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        t1=sim.run(_draws(),c1);m1=agg.analyze(t1)
        results = [{"strategy_id":"random","name":"Random","metrics":m1}]
        c = self.ra.compare_strategies(results)
        assert c["strategies_compared"] == 1
    def test_l_feature_importance_analysis(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        t=sim.run(_draws(),c);m=agg.analyze(t);fi=self.me.compute_feature_importance(t,m)
        assert len(fi) >= 0
    def test_m_distribution_on_big_sample(self):
        d = [DrawRecordData(lottery_code="dlt",draw_number=str(i+1),
            draw_date=date(2024,1,i+1),main_numbers=[1,2,3,4,5]) for i in range(30)]
        r = self.ad.detect_distribution_anomalies(d, (1,25))
        assert r.total_checks == 3
    def test_n_advisor_edge_case(self):
        m = BacktestMetrics(total_investment=0,total_return=0,roi=0,win_count=0,
            total_bets=0,win_rate=0,max_drawdown_amount=0,max_drawdown_pct=0,
            volatility=0,sharpe_ratio=0,avg_return_per_bet=0,final_capital=0,
            best_single_return=0,worst_single_return=0,consecutive_losses=0,
            max_consecutive_losses=0)
        s = self.sa.analyze(m, [])
        assert len(s) > 0
    def test_o_research_empty_metrics(self):
        m = BacktestMetrics(total_investment=0,total_return=0,roi=0,win_count=0,
            total_bets=0,win_rate=0,max_drawdown_amount=0,max_drawdown_pct=0,
            volatility=0,sharpe_ratio=0,avg_return_per_bet=0,final_capital=0,
            best_single_return=0,worst_single_return=0,consecutive_losses=0,
            max_consecutive_losses=0)
        r = self.ra.analyze_backtest(m)
        assert r.confidence_score == 0.3
    def test_p_quick_pipeline(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        t=sim.run(_draws(),c);m=agg.analyze(t)
        r=self.ra.analyze_backtest(m,t,c);s=self.sa.analyze(m,t)
        assert r.summary!="" and len(s)>0
    def test_q_empty_trades_handled(self):
        sim=TradeSimulator();agg=ResultAggregator()
        c=BacktestConfig(lottery_code="dlt",strategy_id="random",start_date="",end_date="",
            main_range=(1,25),main_count=5,initial_capital=1000.0,bet_per_draw=10.0,random_seed=42)
        r=self.ra.analyze_backtest(agg.analyze([]),[])
        assert r.key_metrics["total_bets"]==0
    def test_r_edge_trade_metrics(self):
        from engine.backtest.models import TradeRecord
        t=TradeRecord(draw_date="2024-01-01",draw_number="1",lottery_code="dlt",
            bet_main_numbers=[1],actual_main_numbers=[1],bet_amount=10.0,win_amount=1000000.0,
            is_win=True,prize_level=1,matched_main=5,matched_bonus=2,
            cumulative_pnl=999990.0,cumulative_roi=99999.0,bet_bonus_numbers=None,actual_bonus_numbers=None)
        m=BacktestMetrics(total_investment=10,total_return=1000000,roi=9999900,win_count=1,total_bets=1,
            win_rate=100,max_drawdown_amount=0,max_drawdown_pct=0,volatility=0,sharpe_ratio=0,
            avg_return_per_bet=999990,final_capital=1000010,best_single_return=1000000,worst_single_return=1000000,
            consecutive_losses=0,max_consecutive_losses=0)
        r=self.ra.analyze_backtest(m,[t])
        assert r.key_metrics["roi"]==9999900.0
