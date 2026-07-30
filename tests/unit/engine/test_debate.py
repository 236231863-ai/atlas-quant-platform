"""Tests for Research Debate Engine."""
from __future__ import annotations
import pytest
from engine.debate import ResearchDebateSystem, DebateArgument, DebateReport

class TestDebate:
    def test_argument(self):
        d=ResearchDebateSystem(); a=d.argument("A1","approve","Good approach")
        assert a.agent_id=="A1"; assert a.position=="approve"
    def test_counter_argument(self):
        d=ResearchDebateSystem(); a=d.counter_argument("A2","A1","High risk")
        assert "Disagree" in a.reasoning
    def test_vote(self):
        d=ResearchDebateSystem(); r=d.vote("A1","proposal1"); assert r["votes_cast"]==1
    def test_multiple_votes(self):
        d=ResearchDebateSystem(); d.vote("A1","p1"); d.vote("A1","p2"); r=d.vote("A1","p3")
        assert r["votes_cast"]==3
    def test_final_decision(self):
        d=ResearchDebateSystem(); d.argument("A1","approve","good"); d.vote("A1","p1")
        r=d.final_decision(); assert r.decision in ["approved","rejected"]
    def test_debate_report_fields(self):
        d=ResearchDebateSystem(); d.argument("A1","approve","good"); d.vote("A1","p1")
        r=d.final_decision(); assert r.topic=="research_debate"
    def test_debate_argument(self):
        a=DebateArgument("A1","approve","reasoning"); assert a.agent_id=="A1"
