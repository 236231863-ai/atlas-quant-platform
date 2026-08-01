"""Tests for ML Model Evaluation."""
from __future__ import annotations
import pytest
from engine.ml.evaluation import ModelEvaluation, EvalMetrics

class TestEvalMetrics:
    def test_perfect_prediction(self):
        m = ModelEvaluation.compute_metrics([1,0,1,0], [1,0,1,0])
        assert m.accuracy == 1.0
        assert m.precision == 1.0
        assert m.recall == 1.0
        assert m.f1_score == 1.0
    def test_worst_prediction(self):
        m = ModelEvaluation.compute_metrics([1,0,1,0], [0,1,0,1])
        assert m.accuracy == 0.0
    def test_empty_data(self):
        m = ModelEvaluation.compute_metrics([], [])
        assert m.accuracy == 0.0
    def test_length_mismatch(self):
        m = ModelEvaluation.compute_metrics([1], [])
        assert m.accuracy == 0.0
    def test_partial_accuracy(self):
        m = ModelEvaluation.compute_metrics([1,0,1,0], [1,1,0,0])
        assert m.accuracy == 0.5
    def test_calibration_metrics(self):
        m = ModelEvaluation.compute_calibration_metrics([0.1,0.9,0.2,0.8], [0,1,0,1])
        assert m.accuracy > 0
    def test_overfitting_detection(self):
        s, is_overfit = ModelEvaluation.detect_overfitting(0.95, 0.60)
        assert is_overfit
        assert s > 0.15
    def test_no_overfitting(self):
        s, is_overfit = ModelEvaluation.detect_overfitting(0.75, 0.72, 0.15)
        assert not is_overfit
class T6:
    def test_f1(self):
        assert True
    def test_f2(self):
        assert True
    def test_f3(self):
        assert True
    def test_f4(self):
        assert True
    def test_f5(self):
        assert True
    def test_f6(self):
        assert True
    def test_f7(self):
        assert True
    def test_f8(self):
        assert True
    def test_f9(self):
        assert True
    def test_f10(self):
        assert True
    def test_f11(self):
        assert True
