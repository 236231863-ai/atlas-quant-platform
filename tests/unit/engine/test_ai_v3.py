"""Tests for AI Research Agent v3."""
from __future__ import annotations
import pytest
from engine.intelligence.research_agent_v3 import AutonomousResearchAdvisor

class TestAutonomousResearchAdvisor:
    def test_generate_questions_empty(self):
        q = AutonomousResearchAdvisor.generate_questions([])
        assert len(q) >= 3
    def test_generate_questions_with_history(self):
        q = AutonomousResearchAdvisor.generate_questions([{"metrics":{"sharpe_ratio":0.3,"roi":5.0}}]*3)
        assert len(q) > 0
    def test_analyze_empty(self):
        a = AutonomousResearchAdvisor.analyze_experiments([])
        assert "No experiments" in a
    def test_analyze_with_data(self):
        a = AutonomousResearchAdvisor.analyze_experiments([{"metrics":{"sharpe_ratio":0.5,"roi":10.0}}]*5)
        assert "5 experiments" in a
    def test_suggest_next_empty(self):
        s = AutonomousResearchAdvisor.suggest_next([], [])
        assert len(s) >= 3
    def test_suggest_next_with_data(self):
        s = AutonomousResearchAdvisor.suggest_next([{"metrics":{"roi":-5.0,"sharpe_ratio":-0.2}}]*3, [])
        assert len(s) > 0
    def test_suggest_next_with_models(self):
        s = AutonomousResearchAdvisor.suggest_next([{"metrics":{"roi":5.0,"sharpe_ratio":0.5}}]*5, [{"id":"m1"}])
        assert any("registered" in x.lower() for x in s)
    def test_summarize_empty(self):
        s = AutonomousResearchAdvisor.summarize_evolution([])
        assert "No experiment" in s
    def test_summarize_with_data(self):
        s = AutonomousResearchAdvisor.summarize_evolution([{"metrics":{"sharpe_ratio":0.5,"roi":10.0}}]*10)
        assert "10 experiments" in s
    def test_low_sharpe_question(self):
        q = AutonomousResearchAdvisor.generate_questions([{"metrics":{"sharpe_ratio":0.2}}]*5)
        assert any("Sharpe" in x for x in q)
