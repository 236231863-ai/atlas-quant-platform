"""Tests for Research Director v3."""
from __future__ import annotations
import pytest
from engine.intelligence.research_director_v3 import ResearchDirectorV3

class TestDirectorV3:
    def test_plan_mission(self):
        d=ResearchDirectorV3(); m=d.plan_mission("Improve Sharpe",["Analyze","Test","Deploy"])
        assert m["objective"]=="Improve Sharpe"; assert len(m["subtasks"])==3
    def test_rank_opportunities(self):
        d=ResearchDirectorV3(); disc=[{"target":"a","priority":0.3},{"target":"b","priority":0.9}]
        r=d.rank_opportunities(disc); assert r[0]["target"]=="b"
    def test_manage_portfolio(self):
        d=ResearchDirectorV3(); exps=[{"status":"active"},{"status":"active"},{"status":"completed"}]
        p=d.manage_portfolio(exps,5); assert p["active"]==2; assert p["can_continue"]
    def test_portfolio_budget_exceeded(self):
        d=ResearchDirectorV3(); exps=[{"status":"active"}]*10
        p=d.manage_portfolio(exps,5); assert not p["can_continue"]
    def test_research_roadmap(self):
        d=ResearchDirectorV3(); r=d.research_roadmap("stability")
        assert len(r)==5; assert r[0]=="Analyze stability source"
    def test_list_missions_empty(self):
        assert ResearchDirectorV3().list_missions()==[]
    def test_set_objectives(self):
        d=ResearchDirectorV3(); d.set_objectives(["Obj1","Obj2"]); assert len(d._objectives)==2
