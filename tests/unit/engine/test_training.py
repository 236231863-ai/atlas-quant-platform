"""Tests for Training Pipeline."""
from __future__ import annotations
import pytest
from engine.training import TrainingPipeline, TrainingRun

def feat_fn(d):
    return d
def train_fn(d):
    return "model"
def eval_fn(d, m):
    return {"accuracy": 0.85, "f1": 0.82}

class TestTrainingPipeline:
    def test_create_run(self):
        p = TrainingPipeline(); r = p.create_run("r1","m1","v1",{"lr":0.1})
        assert r.run_id == "r1"; assert r.status == "pending"
    def test_execute_run(self):
        p = TrainingPipeline(); p.set_feature_fn(feat_fn); p.set_train_fn(train_fn); p.set_eval_fn(eval_fn)
        p.create_run("r1","m1","v1",{"lr":0.1}); r = p.execute("r1",[1,2,3])
        assert r.status == "completed"
    def test_execute_nonexistent(self):
        assert TrainingPipeline().execute("nonexistent",[]) is None
    def test_get_run(self):
        p = TrainingPipeline()
        p.create_run("r1","m1","v1",{}); r = p.get_run("r1")
        assert r is not None and r.run_id == "r1"
    def test_list_runs(self):
        p = TrainingPipeline()
        p.create_run("r1","m1","v1",{}); p.create_run("r2","m2","v2",{})
        assert len(p.list_runs()) == 2
    def test_list_by_status(self):
        p = TrainingPipeline(); p.set_feature_fn(feat_fn); p.set_train_fn(train_fn); p.set_eval_fn(eval_fn)
        p.create_run("r1","m1","v1",{}); p.execute("r1",[1]); p.create_run("r2","m2","v2",{})
        completed = p.list_by_status("completed"); pending = p.list_by_status("pending")
        assert len(completed) == 1; assert len(pending) == 1
    def test_count(self):
        p = TrainingPipeline(); p.create_run("r1","m1","v1",{}); assert p.count() == 1
    def test_run_metrics_after_execute(self):
        p = TrainingPipeline(); p.set_feature_fn(feat_fn); p.set_train_fn(train_fn); p.set_eval_fn(eval_fn)
        p.create_run("r1","m1","v1",{}); r = p.execute("r1",[1,2])
        assert r.metrics.get("accuracy", 0) > 0
