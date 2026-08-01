"""Tests for Product Intelligence Layer."""
from __future__ import annotations
import pytest
from engine.product_analytics import EventTracker, ProductMetricsEngine, UserEvent
from backend.user_intelligence import UserProfileEngine
from engine.personal_ai import PersonalResearchAssistant
from backend.community import StrategyCommunity, StrategyPost, StrategyComment
from engine.ranking import ResearchRankEngine, RankScore
from backend.billing import PlanService, PlanType
from engine.growth import ExperimentManager, GrowthExperiment

class TestAnalytics:
    def test_track(self):
        t=EventTracker()
        e=UserEvent("1","u1","USER_LOGIN","now")
        t.track(e)
        assert t.count()==1
    def test_filter(self):
        t=EventTracker(); t.track(UserEvent("1","u1","LOGIN","now")); t.track(UserEvent("2","u1","ANALYSIS","now"))
        assert len(t.get_events("LOGIN"))==1
    def test_dau(self):
        m=ProductMetricsEngine(); e=[UserEvent("1","u1","LOGIN","now"),UserEvent("2","u2","LOGIN","now")]
        assert m.compute_dau(e)==2
class TestProfile:
    def test_analyze(self):
        e=UserProfileEngine(); p=e.analyze_behavior("u1",[{"event_type":"REPORT_VIEW"}]*15)
        assert p.user_type.value=="advanced"
class TestAssistant:
    def test_remember(self):
        a=PersonalResearchAssistant(); a.remember_analysis("u1",{"strategy":"cold"})
        assert len(a.get_history("u1"))==1
class TestCommunity:
    def test_publish(self):
        c=StrategyCommunity(); c.publish(StrategyPost("p1","Alice","cold","test")); assert c.count_posts()==1
class TestRanking:
    def test_leaderboard(self):
        r=ResearchRankEngine(); r.evaluate(RankScore("a",research_quality=0.9)); r.evaluate(RankScore("b",research_quality=0.5))
        lb=r.leaderboard(); assert lb[0]["researcher_id"]=="a"
class TestBilling:
    def test_register(self):
        p=PlanService(); p.register("u1"); assert p.get_subscription("u1").plan==PlanType.FREE
class TestGrowth:
    def test_create(self):
        e=ExperimentManager(); e.create(GrowthExperiment("e1","test",["A","B"],"click_rate")); assert e.count()==1
