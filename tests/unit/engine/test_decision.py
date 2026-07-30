"""Tests for Sprint P7 Decision Intelligence."""
from __future__ import annotations
import pytest
from engine.causal import CausalGraph, CausalAnalyzer, CounterfactualEngine
from engine.decision import DecisionSimulator, DecisionReport
from engine.risk_intelligence import RiskIntelligenceEngine, RiskIntelligenceReport
from engine.opportunity import OpportunityDiscoveryEngine, OpportunityRanking
from engine.memory.decision import DecisionMemorySystem, DecisionRecord
from engine.intelligence.research_director_v9 import ResearchDirectorV9
from engine.dashboard.v10 import DecisionDashboard, DecisionDashboardData
from backend.api.decision import DecisionAPIService

class TestCausal:
    def test_graph_edge(self): g=CausalGraph(); g.add_edge("A","B",0.8); assert g.count_edges()==1
    def test_analyzer(self): r=CausalAnalyzer.analyze("x","y",[(1,2),(2,4),(3,6)]); assert r["cause_score"]>0.5
    def test_counterfactual(self): r=CounterfactualEngine.simulate("price","increase",{}); assert r.confidence>0
class TestDecision:
    def test_simulate(self): r=DecisionSimulator.simulate("test",[{"name":"A","investment":1},{"name":"B","investment":2}]); assert r.goal=="test"
class TestRisk:
    def test_record(self): r=RiskIntelligenceEngine(); r.record_risk("r1",0.5); assert r.count_risks()==1
class TestOpportunity:
    def test_register(self): o=OpportunityDiscoveryEngine(); o.register("op1","tech",0.8,0.7,0.6,0.5); assert o.count()==1
class TestMemory:
    def test_record(self): m=DecisionMemorySystem(); m.record(DecisionRecord("d1","dec","pred","actual",0.8,"lesson")); assert m.count()==1
class TestDirector:
    def test_workflow(self): d=ResearchDirectorV9(); r=d.decision_workflow("goal",[{"name":"A"}]); assert r.goal=="goal"
class TestDashboard:
    def test_summary(self): d=DecisionDashboard(); s=d.summary(); assert s["decisions"]==0
class TestAPI:
    def test_simulate(self): a=DecisionAPIService(); r=a.simulate_decision("g",[{"name":"A"}]); assert a.count()==1
