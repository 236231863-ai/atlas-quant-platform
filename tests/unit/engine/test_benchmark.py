"""Tests for Research Benchmark System."""
from __future__ import annotations
import pytest
from engine.benchmark import ResearchBenchmarkEngine, BenchmarkScore
from engine.backtest.models import BacktestMetrics

def _m(roi=5.0,sharpe=0.5,dd=10.0,vol=1.0,bets=100):
    return BacktestMetrics(500,525,roi,30,bets,30.0,dd*5,dd,vol,sharpe,1.0,525,50,-10,3,3)

class TestBenchmark:
    def test_empty(self):
        s=ResearchBenchmarkEngine.compute(BacktestMetrics(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
        assert s.final_score==0.0
    def test_performance(self):
        s=ResearchBenchmarkEngine.compute(_m(roi=50.0,sharpe=2.0)); assert s.performance>0
    def test_risk(self):
        s=ResearchBenchmarkEngine.compute(_m(dd=5.0,vol=0.3)); assert s.risk>50
    def test_quality(self):
        s=ResearchBenchmarkEngine.compute(_m(),{"stability":90,"complexity":20,"explainability":80,"reproducibility":95})
        assert s.quality>70
    def test_generalization(self):
        s=ResearchBenchmarkEngine.compute(_m(),[0.8,0.7,0.9]); assert s.generalization>0
    def test_final_score_bounded(self):
        s=ResearchBenchmarkEngine.compute(_m(roi=30.0,sharpe=1.5,dd=5.0,vol=0.5),
            [0.85,0.9],{"stability":90,"complexity":20,"explainability":85,"reproducibility":95})
        assert 0<s.final_score<=100
    def test_cross_validate(self):
        s=ResearchBenchmarkEngine.cross_validate([1,2,3,4,5],5)
        assert len(s)==5
    def test_cross_validate_few(self):
        s=ResearchBenchmarkEngine.cross_validate([1,2],5)
        assert len(s)==1
