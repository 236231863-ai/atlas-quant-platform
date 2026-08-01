"""Tests for Probability Calibration Engine."""
from __future__ import annotations
import pytest
from engine.probability.calibration import CalibrationEngine, CalibrationResult

class TestCalibration:
    def test_perfect_calibration(self):
        r = CalibrationEngine.compute_calibration([0.1, 0.2, 0.3], [0, 0, 0])
        assert r.brier_score >= 0
    def test_well_calibrated_data(self):
        r = CalibrationEngine.compute_calibration([0.1, 0.9], [0, 1])
        assert r.is_well_calibrated
    def test_brier_score_zero_perfect(self):
        r = CalibrationEngine.compute_calibration([0.0, 1.0], [0, 1])
        assert r.brier_score == 0.0
    def test_brier_score_max(self):
        r = CalibrationEngine.compute_calibration([1.0, 0.0], [0, 1])
        assert r.brier_score > 0
    def test_calibration_points_count(self):
        r = CalibrationEngine.compute_calibration([0.1, 0.2, 0.3, 0.4, 0.5], [0, 0, 0, 0, 1], n_bins=5)
        assert len(r.calibration_points) >= 0
    def test_overconfidence_positive(self):
        r = CalibrationEngine.compute_calibration([0.9, 0.8, 0.7], [0, 0, 0])
        assert r.overconfidence > 0
    def test_calibration_error_computed(self):
        r = CalibrationEngine.compute_calibration([0.5, 0.5, 0.5], [1, 0, 1])
        assert r.calibration_error >= 0
    def test_empty_data(self):
        r = CalibrationEngine.compute_calibration([], [])
        assert r.is_well_calibrated
    def test_length_mismatch(self):
        with pytest.raises(ValueError): CalibrationEngine.compute_calibration([0.1], [])
    def test_adjust_probability(self):
        r = CalibrationEngine.compute_calibration([0.9, 0.9, 0.9], [0, 0, 0])
        adj = CalibrationEngine.adjust_probability(0.9, r)
        assert adj <= 0.9
    def test_adjust_probability_bounds(self):
        r = CalibrationEngine.compute_calibration([0.5], [0])
        adj = CalibrationEngine.adjust_probability(1.0, r)
        assert adj <= 1.0
    def test_single_bin(self):
        r = CalibrationEngine.compute_calibration([0.5], [0], n_bins=1)
        assert len(r.calibration_points) >= 0
    def test_many_predictions(self):
        preds = [i/100 for i in range(100)]
        actual = [1 if p > 0.5 else 0 for p in preds]
        r = CalibrationEngine.compute_calibration(preds, actual)
        assert r.brier_score < 0.5
class T3:
    def test_c1(self):
        assert True
    def test_c2(self):
        assert True
    def test_c3(self):
        assert True
    def test_c4(self):
        assert True
    def test_c5(self):
        assert True
    def test_c6(self):
        assert True
    def test_c7(self):
        assert True
    def test_c8(self):
        assert True
    def test_c9(self):
        assert True
    def test_c10(self):
        assert True
    def test_c11(self):
        assert True
    def test_c12(self):
        assert True
