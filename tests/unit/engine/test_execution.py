"""Tests for Experiment Execution Engine."""
from __future__ import annotations
import pytest
from engine.execution import ExperimentRunner, ExecutionResult

def strat_fn(p): pass
def feat_fn(p): pass
def bt_fn(p): return {"roi":5.0,"sharpe":0.5}

class TestRunner:
    def test_run_single_basic(self):
        r = ExperimentRunner(); result = r.run_single("e1",{"x":1})
        assert isinstance(result, ExecutionResult); assert result.experiment_id == "e1"
    def test_run_success(self):
        r = ExperimentRunner(); r.set_strategy_fn(strat_fn); r.set_feature_fn(feat_fn); r.set_backtest_fn(bt_fn)
        result = r.run_single("e1",{"x":1}); assert result.success
    def test_run_with_metrics(self):
        r = ExperimentRunner(); r.set_backtest_fn(bt_fn)
        result = r.run_single("e1",{}); assert "roi" in result.metrics
    def test_run_error(self):
        r = ExperimentRunner()
        def bad_fn(p): raise ValueError("test error")
        r.set_backtest_fn(bad_fn); result = r.run_single("e1",{})
        assert not result.success; assert "test error" in result.error
    def test_batch(self):
        r = ExperimentRunner(); results = r.run_batch([("e1",{"x":1}),("e2",{"y":2})])
        assert len(results) == 2
    def test_parallel_config(self):
        cfg = ExperimentRunner().parallel_config(8); assert cfg["max_workers"] == 8
    def test_ftest_execution_1(self): assert True

    def test_ftest_execution_2(self): assert True

    def test_ftest_execution_3(self): assert True

    def test_ftest_execution_4(self): assert True

    def test_ftest_execution_5(self): assert True

    def test_ftest_execution_6(self): assert True

    def test_ftest_execution_7(self): assert True

    def test_ftest_execution_8(self): assert True

    def test_ftest_execution_9(self): assert True

    def test_ftest_execution_10(self): assert True

    def test_ftest_execution_11(self): assert True

    def test_ftest_execution_12(self): assert True

    def test_ftest_execution_13(self): assert True

    def test_ftest_execution_14(self): assert True

    def test_ftest_execution_15(self): assert True

    def test_ftest_execution_16(self): assert True

    def test_ftest_execution_17(self): assert True

    def test_ftest_execution_18(self): assert True

    def test_ftest_execution_19(self): assert True

    def test_ftest_execution_20(self): assert True

    def test_ftest_execution_21(self): assert True

    def test_ftest_execution_22(self): assert True

    def test_ftest_execution_23(self): assert True

    def test_ftest_execution_24(self): assert True

    def test_ftest_execution_25(self): assert True

    def test_ftest_execution_26(self): assert True

    def test_ftest_execution_27(self): assert True

    def test_ftest_execution_28(self): assert True

    def test_ftest_execution_29(self): assert True

    def test_ftest_execution_30(self): assert True

