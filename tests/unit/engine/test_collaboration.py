"""Tests for Multi-Agent Collaboration System."""
from __future__ import annotations
import pytest
from engine.collaboration import ResearchTeamCoordinator, CollaborativeResearchReport

class TestCollaboration:
    def test_register_agent(self):
        c=ResearchTeamCoordinator(); c.register_agent("a1",{}); assert "a1" in c._agents
    def test_assign_task(self):
        c=ResearchTeamCoordinator(); c.register_agent("a1",{}); from engine.agent_protocol import ResearchTask
        assert c.assign_task("a1",ResearchTask("t1","test","T"))
    def test_assign_nonexistent(self):
        from engine.agent_protocol import ResearchTask
        assert not ResearchTeamCoordinator().assign_task("none",ResearchTask("t1","test","T"))
    def test_collect_results(self):
        from engine.agent_protocol import AgentResult
        r=ResearchTeamCoordinator().collect_results([AgentResult("a1","t1",{},0.8),AgentResult("a2","t1",{},0.6)])
        assert r["avg_confidence"]==0.7
    def test_collect_empty(self):
        r=ResearchTeamCoordinator().collect_results([]); assert r["status"]=="no_results"
    def test_resolve_conflict(self):
        r=ResearchTeamCoordinator().resolve_conflict([{"value":0.8},{"value":0.6},{"value":0.3}])
        assert r["decision"]=="approved"; assert r["votes_for"]==2
    def test_resolve_rejected(self):
        r=ResearchTeamCoordinator().resolve_conflict([{"value":0.2},{"value":0.3}])
        assert r["decision"]=="rejected"
    def test_resolve_empty(self):
        r=ResearchTeamCoordinator().resolve_conflict([]); assert r["decision"]=="no_data"
    def test_collaborate(self):
        c=ResearchTeamCoordinator(); c.register_agent("a1",{}); c.register_agent("a2",{})
        r=c.collaborate("Test objective",["a1","a2"]); assert r.confidence>0
    def test_merge_conclusions(self):
        r=ResearchTeamCoordinator().merge_conclusions([{"conclusion":"A"},{"conclusion":"B"}])
        assert "Consensus" in r
