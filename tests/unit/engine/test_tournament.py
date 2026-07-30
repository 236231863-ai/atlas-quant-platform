"""Tests for strategy tournament."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.strategy.registry import StrategyDefinition
from engine.backtest.models import BacktestConfig
from engine.backtest.tournament import StrategyTournament

def _draws(n=10):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1),
        draw_date=date(2024,1,i+1), main_numbers=[i%35+1]*5) for i in range(n)]

STRATS = [
    StrategyDefinition({"strategy_id":"s1","name":"Random","strategy_type":"random","params":{}}),
    StrategyDefinition({"strategy_id":"s2","name":"Cold","strategy_type":"cold","params":{}}),
    StrategyDefinition({"strategy_id":"s3","name":"Hot","strategy_type":"hot","params":{}}),
]

CONFIG = BacktestConfig(lottery_code="dlt", strategy_id="x",
    start_date="", end_date="", main_range=(1,35), main_count=5,
    initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)

class TestTournament:
    def test_initial_state(self):
        t = StrategyTournament()
        assert t is not None
    def test_run_returns_result(self):
        t = StrategyTournament()
        r = t.run(_draws(), CONFIG, STRATS)
        assert r.total_strategies == 3
    def test_ranking_has_unique_ranks(self):
        t = StrategyTournament()
        r = t.run(_draws(10), CONFIG, STRATS)
        ranks = [s.rank for s in r.results]
        assert sorted(ranks) == [1, 2, 3]
    def test_best_strategy_id(self):
        t = StrategyTournament()
        r = t.run(_draws(), CONFIG, STRATS)
        assert r.best_strategy_id in ["s1","s2","s3"]
    def test_each_strategy_has_metrics(self):
        t = StrategyTournament()
        r = t.run(_draws(), CONFIG, STRATS)
        for s in r.results:
            assert s.metrics.total_bets > 0
    def test_markdown_contains_ranking(self):
        t = StrategyTournament()
        r = t.run(_draws(), CONFIG, STRATS)
        md = r.generate_markdown()
        assert "Rank" in md
        assert "Winner" in md
    def test_single_strategy(self):
        t = StrategyTournament()
        r = t.run(_draws(), CONFIG, [STRATS[0]])
        assert r.total_strategies == 1
        assert r.results[0].rank == 1
    def test_empty_draws(self):
        t = StrategyTournament()
        r = t.run([], CONFIG, STRATS)
        assert r.total_strategies == 3
    def test_config_in_result(self):
        t = StrategyTournament(); r = t.run(_draws(), CONFIG, STRATS)
        assert "strategy_id" in r.config
    def test_markdown_has_strategy_names(self):
        t = StrategyTournament(); r = t.run(_draws(), CONFIG, STRATS)
        md = r.generate_markdown()
        assert "Random" in md or "Cold" in md or "Hot" in md
    def test_roi_metric_ranking(self):
        t = StrategyTournament(); r = t.run(_draws(5), CONFIG, STRATS, "roi")
        assert r.ranking_metric == "roi"
    def test_metrics_present(self):
        t = StrategyTournament(); r = t.run(_draws(5), CONFIG, STRATS)
        for s in r.results:
            d = s.to_dict()
            assert "roi" in d
            assert "sharpe_ratio" in d
    def test_reproducible_results(self):
        t1 = StrategyTournament(); t2 = StrategyTournament()
        r1 = t1.run(_draws(), CONFIG, STRATS)
        r2 = t2.run(_draws(), CONFIG, STRATS)
        for a,b in zip(r1.results, r2.results):
            assert a.metrics.roi == b.metrics.roi
    def test_markdown_rankings_ordered(self):
        t = StrategyTournament(); r = t.run(_draws(), CONFIG, STRATS)
        md = r.generate_markdown()
        lines = md.split("\n")
        rank_lines = [l for l in lines if l.startswith("|")]
        assert len(rank_lines) >= 4
