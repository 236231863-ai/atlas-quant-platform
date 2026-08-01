"""Tests for Sprint P15 Trust & Reliability."""
from __future__ import annotations
import pytest
from engine.reliability import ReliabilityEngine
from engine.observability.v2 import TraceEngine, TraceRecord
from engine.resilience import RecoveryEngine
from engine.quality import QualityGateEngine
from engine.release import ReleaseIntelligenceEngine
from engine.security import SecurityAuditEngine
from engine.intelligence.platform_director import PlatformDirector
from engine.dashboard.v18 import V18Dashboard, PlatformAPI

class TestReliability:
    def test_assess(self):
        r=ReliabilityEngine()
        s=r.assess()
        assert s.overall>0
class TestObservability:
    def test_trace(self):
        t=TraceEngine()
        t.record(TraceRecord("t1","api","module_a",["engine"],"agent_a"))
        assert t.count()==1
class TestResilience:
    def test_recover(self):
        r=RecoveryEngine()
        rec=r.auto_recover("api","restart")
        assert rec.status=="recovered"
class TestQuality:
    def test_check(self):
        q=QualityGateEngine()
        r=q.check_release(50,0.85)
        assert r.gate_passed
class TestRelease:
    def test_plan(self):
        r=ReleaseIntelligenceEngine()
        p=r.plan_release("3.5.0",50)
        assert p.risk_score>0
class TestSecurity:
    def test_audit(self):
        s=SecurityAuditEngine()
        r=s.audit()
        assert r.risk_level=="low"
class TestDirector:
    def test_cycle(self):
        d=PlatformDirector()
        r=d.run_platform_cycle()
        assert "reliability" in r
class TestDash:
    def test_summary(self):
        d=V18Dashboard()
        s=d.summary()
        assert "health" in s
class TestAPI:
    def test_record(self):
        a=PlatformAPI()
        a.record_health({"score":0.9})
        assert len(a.get_health_history())==1
