"""Tests for Personality System."""
from __future__ import annotations
import pytest
from engine.agent_personality import PersonalityManager, PersonalityProfile

class TestPersonality:
    def test_create(self):
        m=PersonalityManager(); p=m.create_profile("a1"); assert m.count()==1
    def test_get(self):
        m=PersonalityManager(); m.create_profile("a1"); assert m.get_profile("a1") is not None
    def test_evaluate(self):
        m=PersonalityManager(); m.create_profile("a1",analysis_depth=0.9,confidence_level=0.8)
        e=m.evaluate_behavior("a1","analysis"); assert e["suitability"]>0.5
    def test_adapt(self):
        m=PersonalityManager(); m.create_profile("a1",exploration_level=0.5)
        m.adapt_personality("a1",{"exploration_level":0.2}); assert m.get_profile("a1").exploration_level==0.7
    def test_adapt_invalid(self):
        assert not PersonalityManager().adapt_personality("none",{})
