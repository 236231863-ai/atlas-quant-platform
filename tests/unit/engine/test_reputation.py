"""Tests for Agent Reputation System."""
from __future__ import annotations
import pytest
from engine.reputation import ReputationSystem, AgentReputation

class TestReputation:
    def test_register(self):
        r=ReputationSystem(); r.register("a1"); assert r.count()==1
    def test_increase(self):
        r=ReputationSystem(); r.register("a1"); r.increase("a1","accuracy",0.1); assert r.get("a1").accuracy>0.5
    def test_decrease(self):
        r=ReputationSystem(); r.register("a1"); r.decrease("a1","accuracy",0.1); assert r.get("a1").accuracy<0.5
    def test_increase_bounded(self):
        r=ReputationSystem(); r.register("a1"); r.increase("a1","accuracy",1.0); assert r.get("a1").accuracy<=1.0
    def test_get_rank_bronze(self):
        r=ReputationSystem(); r.register("a1"); assert r.get_rank("a1")=="Bronze"
    def test_get_rank_master(self):
        rep=AgentReputation("a1",0.95,0.95,0.95,0.95,0.95); assert rep.get_rank()=="Master"
    def test_ranking(self):
        r=ReputationSystem(); r.register("a1"); r.increase("a1","accuracy",0.3)
        assert len(r.ranking())==1
    def test_get_nonexistent(self):
        assert ReputationSystem().get("none") is None
