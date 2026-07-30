"""Tests for parameter optimizer."""
from __future__ import annotations
import pytest
from engine.optimizer import grid_search, random_search

class TestGridSearch:
    def test_basic_grid_search(self):
        def objective(params):
            return -(params["x"] ** 2 + params["y"] ** 2)
        result = grid_search(objective, {"x": [-2, 0, 2], "y": [-2, 0, 2]}, maximize=True)
        assert result.best_params == {"x": 0, "y": 0}
        assert result.best_score == 0
    def test_minimization(self):
        def objective(params):
            return params["x"] ** 2
        result = grid_search(objective, {"x": [-5, 0, 5]}, maximize=False)
        assert result.best_params == {"x": 0}
    def test_all_scores_returned(self):
        def objective(params):
            return params["x"]
        result = grid_search(objective, {"x": [1, 2, 3]})
        assert len(result.all_scores) == 3
    def test_param_space_preserved(self):
        def objective(params):
            return 1
        space = {"a": [1, 2], "b": [3, 4]}
        result = grid_search(objective, space)
        assert result.param_space == space
    def test_best_trial_index(self):
        def objective(params):
            return params["x"]
        result = grid_search(objective, {"x": [1, 2, 3]})
        assert result.best_trial_index == 2  # x=3 is best
    def test_n_trials_count(self):
        def objective(params):
            return 1
        result = grid_search(objective, {"x": [1, 2, 3, 4, 5]})
        assert result.n_trials == 5
    def test_single_param(self):
        def objective(params):
            return params["x"]
        result = grid_search(objective, {"x": [10]})
        assert result.best_params == {"x": 10}

class TestRandomSearch:
    def test_basic_random_search(self):
        def objective(params):
            return params["x"]
        result = random_search(objective, {"x": [1, 2, 3, 4, 5]}, n_trials=5, random_seed=42)
        assert len(result.all_scores) == 5
    def test_reproducible_seed(self):
        def objective(p):
            return p["x"]
        r1 = random_search(objective, {"x": list(range(100))}, n_trials=20, random_seed=42)
        r2 = random_search(objective, {"x": list(range(100))}, n_trials=20, random_seed=42)
        assert r1.best_params == r2.best_params
    def test_maximization(self):
        def objective(p):
            return p["x"]
        result = random_search(objective, {"x": [-10, 0, 10]}, n_trials=3, random_seed=1)
        assert result.objective == "maximize"
    def test_minimization(self):
        def objective(p):
            return p["x"]
        result = random_search(objective, {"x": [-10, 0, 10]}, n_trials=3, maximize=False, random_seed=1)
        assert result.objective == "minimize"
    def test_multi_param_grid(self):
        def objective(p): return p["a"] + p["b"]
        r = grid_search(objective, {"a": [1,2], "b": [10,20]})
        assert r.best_params == {"a": 2, "b": 20}
    def test_objective_exception_handled(self):
        def objective(p):
            if p["x"] < 0: raise ValueError("no")
            return p["x"]
        r = grid_search(objective, {"x": [-1, 0, 1]})
        assert len(r.all_scores) == 3
    def test_random_search_more_than_params(self):
        def objective(p): return p["x"]
        r = random_search(objective, {"x": [1,2,3]}, n_trials=10, random_seed=42)
        assert r.n_trials == 10
    def test_random_search_best_found(self):
        calls = []
        def objective(p):
            calls.append(p["x"])
            return p["x"]
        r = random_search(objective, {"x": [100,200,300]}, n_trials=3, random_seed=1)
        assert r.best_score in [100,200,300]
    def test_random_search_best_params_stored(self):
        def objective(p): return p["x"]
        r = random_search(objective, {"x": [100,50,25]}, n_trials=3, random_seed=1)
        assert len(r.best_params) == 1
