"""Tests for Agent Economy Foundation."""
from __future__ import annotations
import pytest
from engine.agent_economy import AgentEconomyEngine, AgentScore

class TestEconomy:
    def test_record_score(self):
        e=AgentEconomyEngine(); e.record_score(AgentScore("a1",0.8,0.7,0.9)); assert len(e.get_scores("a1"))==1
    def test_compute_overall(self):
        s=AgentScore("a1",0.8,0.7,0.9); s.compute(); assert s.overall_score>0.7
    def test_get_latest(self):
        e=AgentEconomyEngine(); e.record_score(AgentScore("a1",0.5,0.5,0.5)); e.record_score(AgentScore("a1",0.9,0.9,0.9))
        assert e.get_latest("a1").performance_score==0.9
    def test_empty_economy(self):
        m=AgentEconomyEngine().get_economy_metrics(); assert m["total_agents"]==0
    def test_economy_metrics(self):
        e=AgentEconomyEngine(); e.record_score(AgentScore("a1",0.8,0.7,0.9)); e.record_score(AgentScore("a2",0.6,0.5,0.7))
        m=e.get_economy_metrics(); assert m["total_agents"]==2
