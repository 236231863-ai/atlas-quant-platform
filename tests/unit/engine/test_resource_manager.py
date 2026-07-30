"""Tests for Research Resource Allocation."""
from __future__ import annotations
import pytest
from engine.resource_manager import ResearchResourceAllocator, AllocationPlan

class TestResource:
    def test_register(self):
        a=ResearchResourceAllocator(); a.register_agent("a1",1.0); assert a.count_agents()==1
    def test_allocate_empty(self):
        a=ResearchResourceAllocator().allocate_experiments(10,{}); assert a.experiments_allowed==0
    def test_allocate(self):
        a=ResearchResourceAllocator(); r=a.allocate_experiments(100,{"a1":0.8,"a2":0.2})
        assert r.experiments_allowed==100; assert len(r.agent_workload)==2
    def test_get_priority(self):
        p=ResearchResourceAllocator().get_priority(0.8,0.7); assert 1<=p<=10
