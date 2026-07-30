"""Tests for Massive Experiment Engine."""
from __future__ import annotations
import pytest
from engine.distributed import ExperimentBatchEngine, BatchExperimentReport

class TestBatch:
    def test_create_batch(self):
        e=ExperimentBatchEngine(); exps=e.create_batch(3,{"x":1},[{"x":2},{"x":3},{"x":4}])
        assert len(exps)==3
    def test_batch_ids(self):
        exps=ExperimentBatchEngine().create_batch(2,{},[{"a":1},{"a":2}])
        assert "batch" in exps[0]["experiment_id"]
    def test_group_by_strategy(self):
        e=ExperimentBatchEngine(); e.create_batch(2,{"strategy":"cold"},[{}])
        e.create_batch(2,{"strategy":"hot"},[{}])
        g=e.group_by_strategy(); assert "cold" in g; assert "hot" in g
    def test_aggregate_empty(self):
        r=ExperimentBatchEngine().aggregate_results([])
        assert r.total_experiments==0
    def test_aggregate_success_rate(self):
        r=ExperimentBatchEngine().aggregate_results([{"success":True,"score":0.8},{"success":False,"score":0.2}])
        assert r.success_rate==0.5
    def test_aggregate_avg_score(self):
        r=ExperimentBatchEngine().aggregate_results([{"success":True,"score":0.8},{"success":True,"score":0.6}])
        assert r.avg_score==0.7
    def test_parallel_config(self):
        c=ExperimentBatchEngine().parallel_config(8)
        assert c["max_workers"]==8; assert c["batch_size"]==80
