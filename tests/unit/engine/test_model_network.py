"""Tests for Model Network."""
from __future__ import annotations
import pytest
from engine.model_network import ModelRegistry, ModelNode, ModelCapabilityProfile

class TestModelNetwork:
    def test_register(self):
        r=ModelRegistry(); r.register(ModelNode("m1","openai",["analysis"])); assert r.count()==1
    def test_remove(self):
        r=ModelRegistry(); r.register(ModelNode("m1","openai",["analysis"])); r.remove("m1"); assert r.count()==0
    def test_evaluate(self):
        r=ModelRegistry(); r.register(ModelNode("m1","openai",["analysis"],cost=1,speed=2,quality_score=0.8))
        e=r.evaluate("m1"); assert e is not None and e>0
    def test_select_best(self):
        r=ModelRegistry(); r.register(ModelNode("m1","a",["analysis"],quality_score=0.7))
        r.register(ModelNode("m2","b",["analysis"],quality_score=0.9))
        b=r.select_best("analysis"); assert b.model_id=="m2"
    def test_select_no_match(self):
        assert ModelRegistry().select_best("nonexistent") is None
