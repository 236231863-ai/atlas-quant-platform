"""Tests for Sprint P5 Product Intelligence."""
from __future__ import annotations
import pytest
from engine.user_intelligence import UserIntelligenceEngine
from engine.personal_ai.v2 import PersonalAIAssistantV2, AIRecommendation
from backend.community.v2 import CommunityPlatformV2, CommunityPost, ResearchPublication
from engine.recommendation_market import RecommendationMarket
from engine.growth_intelligence import GrowthIntelligenceEngine
from apps.mobile import get_mobile_config

class TestUserIntel:
    def test_analyze(self):
        e=UserIntelligenceEngine()
        p=e.analyze_user("u1",[{"type":"analysis"}])
        assert p.level.value=="explorer"
    def test_skill(self):
        e=UserIntelligenceEngine()
        e.analyze_user("u1",[{"type":"analysis"}]*20)
        assert e.calculate_skill_level("u1")==0.7

class TestAIAssistant:
    def test_remember(self):
        a=PersonalAIAssistantV2()
        a.remember("u1",{"type":"analysis"})
        assert len(a.get_history("u1"))==1
    def test_suggest(self):
        a=PersonalAIAssistantV2()
        s=a.suggest("u1")
        assert len(s)==1

class TestCommunity:
    def test_post(self):
        c=CommunityPlatformV2()
        c.publish_post(CommunityPost("p1","Alice","strategy","Test","content"))
        assert c.count_posts()==1
    def test_pub(self):
        c=CommunityPlatformV2()
        c.publish_research(ResearchPublication("r1","Bob","paper","Test","abstract"))
        assert len(c.list_pubs())==1

class TestRecommendation:
    def test_recommend(self):
        m=RecommendationMarket()
        m.register_asset("a1","strategy")
        r=m.recommend("u1")
        assert len(r)>0

class TestGrowth:
    def test_ab(self):
        g=GrowthIntelligenceEngine()
        g.create_ab_test("t1",["A","B"],"click")
        assert g.count_ab_tests()==1

class TestMobile:
    def test_config(self):
        c=get_mobile_config()
        assert c["version"]=="0.1.0"
