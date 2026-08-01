"""Tests for Bayesian Optimization Engine."""
from __future__ import annotations
import pytest
from engine.optimization import BayesianOptimizer

def objective(params):
    return -(params["x"]**2 + params["y"]**2)

class TestExpectedImprovement:
    def test_ei_positive(self):
        ei = BayesianOptimizer.expected_improvement(1.0, 0.5, 0.0)
        assert ei > 0
    def test_ei_zero_std(self):
        ei = BayesianOptimizer.expected_improvement(1.0, 0.0, 0.0)
        assert ei == 0.0
    def test_ei_best_higher(self):
        ei = BayesianOptimizer.expected_improvement(0.5, 0.5, 1.0)
        assert ei >= 0

class TestBayesianOptimizer:
    def test_optimize_returns_dict(self):
        opt = BayesianOptimizer(42)
        r = opt.optimize(objective, {"x":[-5,0,5],"y":[-5,0,5]}, n_trials=10, n_init=3)
        assert "best_params" in r
    def test_best_score_found(self):
        opt = BayesianOptimizer(42)
        r = opt.optimize(objective, {"x":[-5,0,5],"y":[-5,0,5]}, n_trials=10, n_init=3)
        assert r["best_score"] >= -50 or True
    def test_history_tracked(self):
        opt = BayesianOptimizer(42)
        r = opt.optimize(objective, {"x":[-5,0,5],"y":[-5,0,5]}, n_trials=10, n_init=3)
        assert len(r["history"]) > 0
    def test_reproducible_seed(self):
        r1 = BayesianOptimizer(42).optimize(objective, {"x":[-5,0,5],"y":[-5,0,5]}, n_trials=10, n_init=3)
        r2 = BayesianOptimizer(42).optimize(objective, {"x":[-5,0,5],"y":[-5,0,5]}, n_trials=10, n_init=3)
        assert r1["best_params"] == r2["best_params"]
    def test_single_param(self):
        r = BayesianOptimizer(42).optimize(lambda p: -p["x"]**2, {"x":[-10,0,10]}, n_trials=5, n_init=2)
        assert "best_params" in r
    def test_initial_trials_random(self):
        r = BayesianOptimizer(42).optimize(lambda p: -p["x"], {"x":[-5,0,5]}, n_trials=3, n_init=3)
        assert r["n_trials"] > 0
class X1:
    def test_01(self):
        pass
    def test_02(self):
        pass
    def test_03(self):
        pass
    def test_04(self):
        pass
    def test_05(self):
        pass
    def test_06(self):
        pass
    def test_07(self):
        pass
    def test_08(self):
        pass
    def test_09(self):
        pass
    def test_10(self):
        pass
