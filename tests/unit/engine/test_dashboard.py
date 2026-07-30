"""Tests for Research Dashboard Data Layer."""
from __future__ import annotations
import pytest
from engine.dashboard import ResearchDashboardService, DashboardData

class TestDashboard:
    def test_init(self):
        d=ResearchDashboardService(); assert len(d._data.active_experiments)==0
    def test_update_active(self):
        d=ResearchDashboardService(); d.update_active_experiments([{"id":"e1"}])
        assert len(d._data.active_experiments)==1
    def test_update_progress(self):
        d=ResearchDashboardService(); d.update_research_progress(10,50,100)
        assert d._data.research_progress["cycles"]==10; assert d._data.research_progress["discoveries"]==50
    def test_update_strategies(self):
        d=ResearchDashboardService(); d.update_strategy_evolution([{"id":"s1"}])
        assert len(d._data.strategy_evolution)==1
    def test_update_ranking(self):
        d=ResearchDashboardService(); d.update_benchmark_ranking([{"name":"a","score":80},{"name":"b","score":90}])
        assert d._data.benchmark_ranking[0]["name"]=="b"
    def test_update_knowledge(self):
        d=ResearchDashboardService(); d.update_knowledge_growth(100)
        assert d._data.knowledge_growth["total_records"]==100
    def test_summary(self):
        d=ResearchDashboardService(); d.update_active_experiments([{"id":"e1"}])
        d.update_strategy_evolution([{"id":"s1"}])
        d.update_knowledge_growth(50)
        s=d.summary(); assert s["active_experiments"]==1; assert s["knowledge_records"]==50
    def test_get_data(self):
        d=ResearchDashboardService()
        assert isinstance(d.get_data(), DashboardData)
