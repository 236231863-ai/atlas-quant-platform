"""Tests for Research Agent Expansion."""
from __future__ import annotations
import pytest
from engine.agents.expanded import DiscoveryAgent, PatternAgent, StrategyArchitectAgent, ExperimentManagerAgent, BenchmarkAgent, ResearchHistorianAgent, AgentDefinition

class TestAgentsV2:
    def test_discovery_analyze(self):
        a=DiscoveryAgent(); r=a.analyze({"discoveries":[{"recommendation":"test"}]})
        assert r.task_id is not None; assert "test" in r.objective
    def test_discovery_empty(self):
        r=DiscoveryAgent().analyze({"discoveries":[]}); assert r.task_id is not None
    def test_pattern_analyze(self):
        r=PatternAgent().analyze([{"name":"p1"},"{}"]); assert r["patterns_found"]>=1
    def test_strategy_architect(self):
        r=StrategyArchitectAgent().design([{"name":"p1"},{"name":"p2"},{"name":"p3"},{"name":"p4"}])
        assert len(r)==3
    def test_experiment_manager(self):
        r=ExperimentManagerAgent().plan([{"id":"s1"},{"id":"s2"}]); assert r["experiments_planned"]==2
    def test_benchmark(self):
        r=BenchmarkAgent().evaluate([{"score":0.8},{"score":0.6}]); assert r["avg_score"]==0.7
    def test_historian(self):
        r=ResearchHistorianAgent().summarize([{"id":"e1"}]); assert "historian" in r
    def test_agent_definition(self):
        d=AgentDefinition("a1","Test","desc",["in"],["out"]); assert d.agent_id=="a1"
