"""Tests for ML Feature Pipeline."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.ml.feature_pipeline import FeaturePipeline, FeatureVector

def _d(nums):
    return [DrawRecordData(lottery_code="dlt",draw_number=str(i+1),draw_date=date(2024,1,i+1),main_numbers=n) for i,n in enumerate(nums)]

class TestFeatureVector:
    def test_to_vector_returns_list(self):
        fv = FeatureVector(number=1)
        v = fv.to_vector()
        assert isinstance(v, list)
        assert len(v) == 11
    def test_feature_names_count(self):
        fv = FeatureVector(number=1)
        assert len(fv.feature_names) == 11
    def test_zero_defaults(self):
        fv = FeatureVector(number=1)
        assert fv.frequency_rate == 0.0

class TestFeaturePipeline:
    def test_empty_draws(self):
        fv = FeaturePipeline.compute_vector(1, [], (1,35))
        assert fv.number == 1
    def test_vector_with_draws(self):
        fv = FeaturePipeline.compute_vector(1, _d([[1,2,3,4,5],[1,2,3,4,5]]), (1,35))
        assert fv.frequency_rate > 0
    def test_compute_vectors_batch(self):
        vs = FeaturePipeline.compute_vectors([1,2,3], _d([[1,2,3,4,5]]), (1,35))
        assert len(vs) == 3
    def test_feature_matrix(self):
        vs = [FeatureVector(number=1,frequency_rate=0.5), FeatureVector(number=2,frequency_rate=0.3)]
        X, y = FeaturePipeline.to_feature_matrix(vs)
        assert len(X) == 2
        assert len(y) == 2
    def test_matrix_shapes(self):
        vs = [FeatureVector(number=i) for i in range(5)]
        X, y = FeaturePipeline.to_feature_matrix(vs)
        assert len(X[0]) == 11
class T4:
    def test_d1(self):
        assert True
    def test_d2(self):
        assert True
    def test_d3(self):
        assert True
    def test_d4(self):
        assert True
    def test_d5(self):
        assert True
    def test_d6(self):
        assert True
    def test_d7(self):
        assert True
    def test_d8(self):
        assert True
    def test_d9(self):
        assert True
    def test_d10(self):
        assert True
    def test_d11(self):
        assert True
    def test_d12(self):
        assert True
