"""Tests for Institution."""
from __future__ import annotations
import pytest
from engine.institution.governance import ResearchGovernanceEngine, ResearchPolicy
from engine.institution.departments import ResearchDepartmentManager, ResearchDepartment
from engine.institution.career import ResearchCareerManager, ScientistProfile, CareerLevel
from engine.publication import ResearchPublicationSystem, Publication

class TestGovernance:
    def test_create_policy(self):
        g=ResearchGovernanceEngine(); g.create_policy(ResearchPolicy("p1","Policy",["rule1"],"all"))
        assert g.count()==1
    def test_evaluate_compliance(self):
        g=ResearchGovernanceEngine(); g.create_policy(ResearchPolicy("p1","P",["rule1"],"all"))
        r=g.evaluate_compliance({"activity":"rule1"}); assert r["compliant"]
    def test_approve(self):
        assert ResearchGovernanceEngine().approve_research("p1")

class TestDepartments:
    def test_create(self):
        m=ResearchDepartmentManager(); m.create(ResearchDepartment("d1","Prob","probability")); assert m.count()==1
    def test_assign(self):
        m=ResearchDepartmentManager(); m.create(ResearchDepartment("d1","Prob","probability"))
        m.assign_agent("d1","a1"); assert len(m.list_departments()[0].members)==1

class TestCareer:
    def test_register(self):
        m=ResearchCareerManager(); m.register(ScientistProfile("s1","Alice")); assert m.count()==1
    def test_promote(self):
        m=ResearchCareerManager()
        m.register(ScientistProfile("s1","Alice",research_quality=0.6,innovation_score=0.6,publication_score=0.6,teamwork_score=0.6))
        r=m.promote("s1"); assert r; assert m.list_scientists()[0].level==CareerLevel.RESEARCH

class TestPublication:
    def test_generate(self):
        p=ResearchPublicationSystem(); p.generate(Publication("p1","Test","Alice")); assert p.count()==1
    def test_publish(self):
        p=ResearchPublicationSystem(); p.generate(Publication("p1","Test","Alice"))
        p.review("p1",0.8); assert p.publish("p1")
