"""Tests for Continuous Research Loop."""
from __future__ import annotations
import pytest
from engine.research.loop import ContinuousResearchLoop, ResearchCycleRecord

class TestLoop:
    def test_simulate_cycle(self):
        l=ContinuousResearchLoop(); r=l.simulate_cycle(3,5)
        assert r.discoveries==3; assert r.experiments_created==5
    def test_cycle_count(self):
        l=ContinuousResearchLoop(); l.simulate_cycle(); assert l.count()==1
    def test_multiple_cycles(self):
        l=ContinuousResearchLoop(); l.simulate_cycle(); l.simulate_cycle(); assert l.count()==2
    def test_weekly_summary_empty(self):
        assert "No research" in ContinuousResearchLoop().weekly_summary()
    def test_weekly_summary_with_data(self):
        l=ContinuousResearchLoop(); l.simulate_cycle(2,10); s=l.weekly_summary()
        assert "1 cycles" in s; assert "2 discoveries" in s
    def test_cycle_history(self):
        l=ContinuousResearchLoop(); l.simulate_cycle(); assert len(l.cycle_history())==1
    def test_cycle_record_fields(self):
        r=ResearchCycleRecord("c1","test",1,2,2,0.5)
        assert r.cycle_id=="c1"; assert r.avg_score==0.5
