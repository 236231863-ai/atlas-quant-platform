"""Tests for Research Discovery Engine."""
from __future__ import annotations
import pytest
from engine.discovery import ResearchDiscoveryEngine, DiscoveryReport

class TestDiscovery:
    def test_empty_features(self):
        assert ResearchDiscoveryEngine.detect_feature_anomalies([],{})==[]
    def test_no_anomaly(self):
        h=[{"gap":0.5,"entropy":0.3}]*10; r=ResearchDiscoveryEngine.detect_feature_anomalies(h,{"gap":0.5,"entropy":0.3})
        assert len(r)==0
    def test_anomaly_detected(self):
        h=[{"gap":0.5}]*10; r=ResearchDiscoveryEngine.detect_feature_anomalies(h,{"gap":0.9})
        assert len(r)>=1
    def test_anomaly_z_score(self):
        h=[{"gap":0.5}]*10; r=ResearchDiscoveryEngine.detect_feature_anomalies(h,{"gap":0.9})
        assert abs(r[0]["z_score"])>0
    def test_anomaly_direction(self):
        h=[{"gap":0.5}]*10; r=ResearchDiscoveryEngine.detect_feature_anomalies(h,{"gap":0.9})
        assert r[0]["direction"]=="increase"
    def test_strategy_degradation_insufficient(self):
        assert ResearchDiscoveryEngine.detect_strategy_degradation([{"sharpe_ratio":0.5}],10)==[]
    def test_degradation_detected(self):
        h=[{"sharpe_ratio":1.0}]*20+[{"sharpe_ratio":0.3}]*20
        r=ResearchDiscoveryEngine.detect_strategy_degradation(h,10)
        assert len(r)>=1
    def test_drawdown_detected(self):
        h=[{"sharpe_ratio":0.5,"max_drawdown":5}]*10+[{"sharpe_ratio":0.5,"max_drawdown":30}]*10
        r=ResearchDiscoveryEngine.detect_strategy_degradation(h,10)
        assert any(x["type"]=="drawdown_increase" for x in r)
    def test_score_opportunity(self):
        r=ResearchDiscoveryEngine.score_opportunity([{"feature":"gap","z_score":3.0,"direction":"up"}],[])
        assert r.total_opportunities>=1
    def test_score_with_degradation(self):
        r=ResearchDiscoveryEngine.score_opportunity([],[{"type":"sharpe_decline","decline_pct":30}])
        assert r.total_opportunities>=1
    def test_top_priority(self):
        r=ResearchDiscoveryEngine.score_opportunity([{"feature":"a","z_score":4.0,"direction":"up"}],[])
        assert r.top_priority>0
