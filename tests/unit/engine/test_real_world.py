"""Tests for Sprint P6 Real World Intelligence."""
from __future__ import annotations
import pytest
from engine.intelligence_data import DataIntelligenceHub, DataSource, DataLineage
from engine.news_intelligence import NewsIntelligenceEngine, NewsInsight
from engine.knowledge_fusion import KnowledgeFusionEngine, FusedKnowledge
from engine.signal import SignalGenerator, ResearchSignal
from engine.environment import EnvironmentSimulator
from engine.intelligence.research_director_v8 import ResearchDirectorV8

class TestDataHub:
    def test_source(self): h=DataIntelligenceHub(); h.register_source(DataSource("s1","API","web",0.8)); assert h.count_sources()==1
    def test_lineage(self): h=DataIntelligenceHub(); h.record_lineage(DataLineage("l1","API","pipeline","engine")); assert h.count_lineage()==1

class TestNews:
    def test_insight(self): n=NewsIntelligenceEngine(); n.record_insight(NewsInsight("n1","event","policy")); assert n.count()==1

class TestFusion:
    def test_fuse(self): k=KnowledgeFusionEngine(); k.fuse(FusedKnowledge("f1","ent",["s1"])); assert k.count()==1

class TestSignal:
    def test_generate(self): s=SignalGenerator(); s.generate(ResearchSignal("sig1","trend","test")); assert s.count()==1

class TestEnv:
    def test_scenario(self): e=EnvironmentSimulator(); e.create_scenario("test","high",0.8); assert e.count()==1

class TestDirector:
    def test_observe(self): d=ResearchDirectorV8(); r=d.observe_world([{"type":"change","severity":"high"}]); assert r["observations"]==1
