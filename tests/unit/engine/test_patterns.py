"""Tests for Pattern Mining Engine."""
from __future__ import annotations
import pytest
from engine.patterns import PatternMiningEngine, ResearchPattern

class TestPatterns:
    def test_empty_correlations(self):
        assert PatternMiningEngine.discover_correlations([])==[]
    def test_correlation_discovered(self):
        fm=[{"gap":0.5,"entropy":0.3,"sharpe_ratio":0.8},{"gap":0.3,"entropy":0.7,"sharpe_ratio":0.4}]
        r=PatternMiningEngine.discover_correlations(fm,"sharpe_ratio")
        assert len(r)>0
    def test_correlation_values(self):
        fm=[{"a":1,"b":2,"sharpe":0.8},{"a":2,"b":1,"sharpe":0.4},{"a":3,"b":0,"sharpe":0.2}]
        r=PatternMiningEngine.discover_correlations(fm,"sharpe")
        for c in r: assert -1<=c["correlation"]<=1
    def test_extract_success(self):
        exps=[{"metrics":{"sharpe_ratio":0.8},"params":{"gap":10,"entropy":0.5}}]
        r=PatternMiningEngine.extract_success_patterns(exps,0.5)
        assert len(r)==1
    def test_success_threshold(self):
        exps=[{"metrics":{"sharpe_ratio":0.3},"params":{"gap":10}}]
        assert len(PatternMiningEngine.extract_success_patterns(exps,0.5))==0
    def test_extract_failure(self):
        exps=[{"metrics":{"sharpe_ratio":-0.5},"params":{"gap":5}}]
        r=PatternMiningEngine.extract_failure_patterns(exps,-0.3)
        assert len(r)==1
    def test_failure_threshold(self):
        exps=[{"metrics":{"sharpe_ratio":0.1},"params":{"gap":5}}]
        assert len(PatternMiningEngine.extract_failure_patterns(exps,-0.3))==0
    def test_pattern_fields(self):
        p=ResearchPattern("p1","test","success","positive",0.8,["gap"])
        assert p.pattern_id=="p1"; assert p.confidence==0.8
    def test_pattern_to_dict(self):
        p=ResearchPattern("p1","test","success","positive",0.8,["gap"])
        d=p.to_dict(); assert d["pattern_id"]=="p1"
