"""Tests for Sprint P8 Action & Feedback Intelligence."""
from __future__ import annotations
import pytest
from engine.action import ActionPlanner
from engine.execution_intelligence import ExecutionSimulator
from engine.feedback import FeedbackIntelligence, FeedbackInsight
from engine.adaptation import AdaptiveStrategyEngine
from engine.workflow import AutonomousWorkflowEngine
from engine.intelligence.research_director_v10 import ResearchDirectorV10
from engine.dashboard.v11 import AutonomousDashboard, AutonomousDashboardData
from backend.api.action import ActionAPIService

class TestAction:
    def test_create(self):
        a=ActionPlanner()
        r=a.create_plan("goal",["s1","s2"])
        assert r.goal=="goal"
    def test_count(self):
        a=ActionPlanner()
        a.create_plan("g",["s1"])
        assert a.count()==1
class TestExecution:
    def test_simulate(self):
        e=ExecutionSimulator()
        r=e.simulate("p1",3)
        assert r.success_probability>0
class TestFeedback:
    def test_record(self):
        f=FeedbackIntelligence()
        f.record(FeedbackInsight("f1","pred","act","res",0.1))
        assert f.count()==1
class TestAdaptation:
    def test_adjust(self):
        a=AdaptiveStrategyEngine()
        r=a.adjust_parameter("gap",0.5,0.2)
        assert r.after!=0.5
class TestWorkflow:
    def test_create(self):
        w=AutonomousWorkflowEngine()
        wi=w.create("d1")
        assert wi.state=="CREATED"
class TestDirector:
    def test_cycle(self):
        d=ResearchDirectorV10()
        r=d.autonomous_cycle("g",["s1","s2"])
        assert "plan" in r
class TestDashboard:
    def test_summary(self):
        d=AutonomousDashboard()
        s=d.summary()
        assert s["actions"]==0
class TestAPI:
    def test_create(self):
        a=ActionAPIService()
        r=a.create_plan("g",["s1"])
        assert r.goal=="g"
