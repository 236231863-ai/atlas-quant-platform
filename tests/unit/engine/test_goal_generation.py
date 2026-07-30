"""Tests for Goal Generator."""
from __future__ import annotations
import pytest
from engine.goal_generation import ResearchGoalGenerator, ResearchGoal

class TestGoalGen:
    def test_generate(self):
        g=ResearchGoalGenerator(); r=g.generate_goal(ResearchGoal("g1","Test","reason"))
        assert g.count()==1
    def test_rank(self):
        g=ResearchGoalGenerator(); g.generate_goal(ResearchGoal("g1","A","r",priority=0.3,expected_value=0.4))
        g.generate_goal(ResearchGoal("g2","B","r",priority=0.9,expected_value=0.8))
        r=g.rank_goals(); assert r[0].goal_id=="g2"
    def test_merge(self):
        g=ResearchGoalGenerator(); g.generate_goal(ResearchGoal("g1","A","r1")); g.generate_goal(ResearchGoal("g2","B","r2"))
        m=g.merge_goals("g1","g2"); assert m is not None and "A" in m.title
    def test_evaluate(self):
        g=ResearchGoalGenerator(); g.generate_goal(ResearchGoal("g1","A","r",priority=0.8,expected_value=0.7,risk=0.2))
        e=g.evaluate_goal("g1"); assert e["overall_score"]>0
    def test_list(self):
        g=ResearchGoalGenerator(); g.generate_goal(ResearchGoal("g1","A","r")); assert len(g.list_goals())==1
