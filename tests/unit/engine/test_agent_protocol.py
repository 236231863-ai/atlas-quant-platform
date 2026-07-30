"""Tests for Agent Communication Protocol."""
from __future__ import annotations
import pytest
from engine.agent_protocol import AgentProtocol, ResearchTask, ResearchMessage, AgentResult, AgentFeedback

class TestProtocol:
    def test_create_task(self):
        p=AgentProtocol(); t=ResearchTask("t1","analysis","Test"); p.create_task(t); assert p.count_tasks()==1
    def test_get_task(self):
        p=AgentProtocol(); p.create_task(ResearchTask("t1","a","T")); assert p.get_task("t1") is not None
    def test_send_message(self):
        p=AgentProtocol(); m=ResearchMessage("m1","A","B","hello"); p.send_message(m); assert p.count_messages()==1
    def test_receive_messages(self):
        p=AgentProtocol(); p.send_message(ResearchMessage("m1","A","B","hi")); assert len(p.receive_messages("B"))==1
    def test_receive_filter(self):
        p=AgentProtocol(); p.send_message(ResearchMessage("m1","A","B","hi")); assert len(p.receive_messages("C"))==0
    def test_trace_history(self):
        p=AgentProtocol(); p.send_message(ResearchMessage("m1","A","B","hi",task_id="t1"))
        assert len(p.trace_history("t1"))==1
    def test_validate_valid(self):
        m=ResearchMessage("m1","A","B","ok"); assert AgentProtocol().validate_message(m)==[]
    def test_validate_invalid(self):
        m=ResearchMessage("","","",""); assert len(AgentProtocol().validate_message(m))>0
    def test_agent_result(self):
        r=AgentResult("a1","t1",{"score":0.8}); assert r.agent_id=="a1"; assert r.confidence==0.5
    def test_agent_feedback(self):
        f=AgentFeedback("a1","a2","review","good"); assert f.feedback_type=="review"
