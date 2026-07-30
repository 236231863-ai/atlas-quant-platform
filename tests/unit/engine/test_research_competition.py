"""Tests for Research Competition System."""
from __future__ import annotations
import pytest
from engine.research_competition import ResearchCompetitionEngine, CompetitionReport

class TestCompetition:
    def test_create(self):
        c=ResearchCompetitionEngine(); r=c.create_competition("c1"); assert r["status"]=="created"
    def test_evaluate_empty(self):
        r=ResearchCompetitionEngine().evaluate([]); assert r.type=="none"
    def test_evaluate_winner(self):
        entries=[{"entry_id":"e1","name":"A","performance":0.9,"risk":0.2,"innovation":0.8,"stability":0.7},
                 {"entry_id":"e2","name":"B","performance":0.5,"risk":0.5,"innovation":0.5,"stability":0.5}]
        r=ResearchCompetitionEngine().evaluate(entries); assert r.winner=="A"
    def test_avg_score(self):
        entries=[{"entry_id":"e1","name":"A","performance":0.8,"risk":0.2,"innovation":0.7,"stability":0.6}]
        r=ResearchCompetitionEngine().evaluate(entries); assert r.avg_score>0
    def test_history(self):
        c=ResearchCompetitionEngine(); c.create_competition("c1"); assert len(c.history())==1
