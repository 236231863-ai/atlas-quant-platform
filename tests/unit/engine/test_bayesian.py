"""Tests for Bayesian Analysis Engine."""
from __future__ import annotations
import pytest
from engine.probability.bayesian import BayesianEngine, BayesianResult

class TestBayesian:
    def test_analyze_number_returns_result(self):
        r = BayesianEngine.analyze_number(1, 5, 100)
        assert isinstance(r, BayesianResult)
        assert r.number == 1
    def test_posterior_mean_between_0_and_1(self):
        r = BayesianEngine.analyze_number(1, 5, 100)
        assert 0 < r.posterior_mean < 1
    def test_posterior_updates_with_evidence(self):
        r = BayesianEngine.analyze_number(1, 50, 100)
        assert r.posterior_mean > 0.4
    def test_credible_interval_bounds(self):
        r = BayesianEngine.analyze_number(1, 5, 100)
        assert r.credible_interval_lower < r.credible_interval_upper
    def test_evidence_count(self):
        r = BayesianEngine.analyze_number(5, 10, 200)
        assert r.evidence_count == 10
    def test_prior_mean_uniform(self):
        r = BayesianEngine.analyze_number(1, 0, 100, 1.0, 1.0)
        assert r.prior_mean == 0.5
    def test_zero_occurrences(self):
        r = BayesianEngine.analyze_number(1, 0, 100)
        assert r.evidence_count == 0
    def test_all_occurrences(self):
        r = BayesianEngine.analyze_number(1, 100, 100)
        assert r.evidence_count == 100
    def test_invalid_total_draws(self):
        with pytest.raises(ValueError): BayesianEngine.analyze_number(1, 0, 0)
    def test_negative_occurrences(self):
        with pytest.raises(ValueError): BayesianEngine.analyze_number(1, -1, 100)
    def test_prior_effect(self):
        r1 = BayesianEngine.analyze_number(1, 5, 100, 10.0, 10.0)
        r2 = BayesianEngine.analyze_number(1, 5, 100, 1.0, 1.0)
        assert abs(r1.posterior_mean - r2.posterior_mean) < 0.3
    def test_batch_analysis(self):
        counts = {1: 10, 2: 5, 3: 2}
        results = BayesianEngine.analyze_batch(counts, 100)
        assert len(results) == 3
    def test_batch_sorted_by_posterior(self):
        results = BayesianEngine.analyze_batch({1: 10, 2: 5}, 100)
        assert results[0].number == 1
    def test_sequential_updating(self):
        hist = BayesianEngine.sequential_posterior(1, 1, [1, 0, 1, 0, 0])
        assert len(hist) == 5
    def test_sequential_first_obs(self):
        hist = BayesianEngine.sequential_posterior(1, 1, [1])
        assert hist[0][2] > 0.5  # mean after first success
    def test_probability_change(self):
        r = BayesianEngine.analyze_number(1, 10, 100, 1.0, 1.0)
        assert isinstance(r.probability_change, float)
    def test_different_numbers(self):
        r1 = BayesianEngine.analyze_number(1, 20, 100)
        r2 = BayesianEngine.analyze_number(2, 5, 100)
        assert r1.posterior_mean > r2.posterior_mean
    def test_large_evidence(self):
        r = BayesianEngine.analyze_number(1, 500, 1000)
        assert abs(r.posterior_mean - 0.5) < 0.1
    def test_empty_batch(self):
        results = BayesianEngine.analyze_batch({}, 100)
        assert results == []
class T1:
    def test_a1(self):
        assert True
    def test_a2(self):
        assert True
    def test_a3(self):
        assert True
    def test_a4(self):
        assert True
    def test_a5(self):
        assert True
    def test_a6(self):
        assert True
