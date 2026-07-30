"""Tests for Strategy Factory."""
from __future__ import annotations
import pytest
from engine.strategy_generator import StrategyCandidate
from engine.strategy_generator.factory import StrategyFactory, StrategyTemplate

class TestFactory:
    def test_register_template(self):
        f=StrategyFactory(); t=StrategyTemplate("t1","Test","gap_based",{"gap":int})
        f.register_template(t); assert f.count_templates()==1
    def test_generate_from_pattern(self):
        f=StrategyFactory(); c=f.generate_from_pattern("success",["entropy","gap"])
        assert len(c)==2
    def test_candidate_fields(self):
        c=StrategyFactory().generate_from_pattern("test",["gap"])
        assert c[0].source=="strategy_factory"
    def test_mutate_params(self):
        f=StrategyFactory(); c=StrategyCandidate("s1","T","gap_based",{"gap":10})
        m=f.mutate_parameters(c,0.1); assert m.params["gap"]==11.0
    def test_mutation_confidence(self):
        f=StrategyFactory(); c=StrategyCandidate("s1","T","gap_based",{},confidence=0.8)
        m=f.mutate_parameters(c,0.1); assert m.confidence<0.8
    def test_crossover(self):
        f=StrategyFactory(); a=StrategyCandidate("a","A","gap_based",{"gap":10},confidence=0.6)
        b=StrategyCandidate("b","B","gap_based",{"entropy":0.5},confidence=0.8)
        c=f.crossover(a,b); assert "gap" in c.params; assert "entropy" in c.params
    def test_cross_confidence_avg(self):
        f=StrategyFactory(); a=StrategyCandidate("a","A","gap",{},confidence=0.6)
        b=StrategyCandidate("b","B","gap",{},confidence=0.8)
        c=f.crossover(a,b); assert c.confidence==0.7
    def test_list_templates(self):
        f=StrategyFactory(); assert f.list_templates()==[]
