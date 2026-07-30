"""Tests for Sprint P9 Real World Validation."""
from __future__ import annotations
import pytest
from engine.observability import SystemObservabilityEngine, SystemHealthReport
from engine.evaluation import IntelligenceEvaluationEngine, IntelligenceScore
from engine.user_feedback import UserFeedbackEngine, UserAction
from engine.autonomous_maintenance import AutonomousMaintenanceEngine
from engine.reality_learning import RealityLearningEngine, PredictionRecord
from engine.intelligence.research_director_v11 import ResearchDirectorV11
from engine.dashboard.v12 import ProductionDashboard, ProductionDashboardData
from backend.api.operation import OperationAPIService

class TestObs:
    def test_health(self): o=SystemObservabilityEngine(); r=o.check_health(); assert r.healthy
    def test_modules(self): o=SystemObservabilityEngine(); m=o.analyze_modules(); assert len(m)>0
class TestEval:
    def test_score(self): e=IntelligenceEvaluationEngine(); s=e.evaluate_prediction(0.8,0.7,0.9); assert s.overall>0
class TestFeedback:
    def test_action(self): u=UserFeedbackEngine(); u.record_action(UserAction("a1","u1","view_report","r1")); assert u.count_actions()==1
class TestMaint:
    def test_check(self): m=AutonomousMaintenanceEngine(); r=m.health_check(); assert r.health_score>0
class TestReality:
    def test_record(self): r=RealityLearningEngine(); r.record(PredictionRecord("p1","up","up",0.1,"correct")); assert r.count()==1
class TestDirector:
    def test_cycle(self): d=ResearchDirectorV11(); r=d.run_operation_cycle(); assert "health" in r
class TestDashboard:
    def test_summary(self): d=ProductionDashboard(); s=d.summary(); assert "health" in s
class TestAPI:
    def test_health(self): a=OperationAPIService(); r=a.get_health(); assert r.healthy
