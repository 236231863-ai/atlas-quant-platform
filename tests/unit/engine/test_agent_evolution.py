"""Tests for Agent Evolution Engine."""
from __future__ import annotations
import pytest
from engine.evolution.agent import AgentEvolutionEngine, AgentVersion

class TestAgentEvolution:
    def test_record_version(self):
        e=AgentEvolutionEngine(); e.record_version(AgentVersion("a1",1,{"analysis":0.8},{})); assert len(e.get_versions("a1"))==1
    def test_skill_mutation(self):
        e=AgentEvolutionEngine(); e.record_version(AgentVersion("a1",1,{"skill":0.5},{}))
        v=e.skill_mutation("a1",{"skill":0.5},0.2); assert v.skills["skill"]==0.6
    def test_latest_version(self):
        e=AgentEvolutionEngine(); e.record_version(AgentVersion("a1",1,{},{})); e.record_version(AgentVersion("a1",2,{},{}))
        assert e.latest_version("a1").version==2
    def test_evolution_history(self):
        e=AgentEvolutionEngine(); e.record_version(AgentVersion("a1",1,{},{})); assert len(e.evolution_history("a1"))==1
    def test_empty_history(self):
        assert AgentEvolutionEngine().get_versions("none")==[]
