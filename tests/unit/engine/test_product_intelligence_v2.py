"""Tests for Sprint P10 v3.0.0."""
from __future__ import annotations
import pytest
from engine.user_behavior import UserBehaviorEvent, BehaviorAnalyzer
from engine.user_profile import ProfileEvolutionEngine
from engine.product_learning import FeedbackLearningEngine, ProductKnowledgeBase
from engine.intelligence.product_director import AIProductDirector, FeatureRecommendation
from engine.product_experiment import ProductExperimentEngine, ProductExperiment
from engine.product_evolution import ProductEvolutionEngine
from engine.business_intelligence import BusinessIntelligenceEngine
from engine.dashboard.v13 import V13Dashboard, ProductIntelligenceAPI

class TestBehavior:
    def test_record(self): a=BehaviorAnalyzer(); e=UserBehaviorEvent("u1","login","auth",1.0,"success","ok"); a.record(e); assert a.count()==1
    def test_churn(self): a=BehaviorAnalyzer(); [a.record(UserBehaviorEvent("u1","analysis_start","f1")) for _ in range(5)]; assert a.churn_risk("u1")<0.5
class TestProfile:
    def test_update(self): p=ProfileEvolutionEngine(); pr=p.update_profile("u1",[{"event_type":"analysis_complete"}]*50); assert pr.level.value=="RESEARCHER"
class TestLearning:
    def test_learn(self): l=FeedbackLearningEngine(); l.learn("gap_analysis",True); l.learn("gap_analysis",True); assert l.get_kb().count()==1
class TestProductDirector:
    def test_roadmap(self): d=AIProductDirector(); r=d.generate_roadmap([FeatureRecommendation("f1",5,0.8,0.3,0.2),FeatureRecommendation("f2",3,0.5,0.7,0.5)]); assert r[0].feature=="f1"
class TestExperiment:
    def test_create(self): e=ProductExperimentEngine(); e.create(ProductExperiment("e1","test","feature",["A","B"])); assert e.count()==1
class TestEvolution:
    def test_analyze(self): e=ProductEvolutionEngine(); r=e.analyze_modules({"mod1":0.8,"mod2":0.5,"mod3":0.3,"mod4":0.1}); assert len(r.keep)==1
class TestBusiness:
    def test_revenue(self): b=BusinessIntelligenceEngine(); r=b.analyze_revenue(["u1","u2"],{"pro":100}); assert r["total_users"]==2
class TestDashboard:
    def test_summary(self): d=V13Dashboard(); s=d.summary(); assert "users" in s
class TestAPI:
    def test_record(self): a=ProductIntelligenceAPI(); a.record_profile({"user_id":"u1"}); assert a.get_user_profile("u1") is not None
