"""Tests for entropy feature computation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.features.entropy_features import compute_entropy_features

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

class TestEntropyFeatures:
    def test_empty(self):
        r = compute_entropy_features([], (1,35))
        assert r["total_draws"] == 0
    def test_shannon_entropy_computed(self):
        r = compute_entropy_features(_d([[1]*5,[2]*5,[3]*5]), (1,35))
        assert r["features"]["shannon_entropy"] > 0
    def test_uniform_higher_entropy(self):
        uniform = _d([[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15]])
        skewed = _d([[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5]])
        ru = compute_entropy_features(uniform, (1,35))
        rs = compute_entropy_features(skewed, (1,35))
        assert ru["features"]["shannon_entropy"] > rs["features"]["shannon_entropy"]
    def test_normalized_entropy(self):
        r = compute_entropy_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["features"]["normalized_entropy"] > 0
    def test_evenness(self):
        r = compute_entropy_features(_d([[1,2,3,4,5]]), (1,35))
        assert "evenness" in r["features"]
    def test_uniformity_pct(self):
        r = compute_entropy_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["features"]["uniformity_pct"] >= 0
    def test_draw_entropy_mean(self):
        r = compute_entropy_features(_d([[1,2,3,4,5],[6,7,8,9,10]]), (1,35))
        assert r["features"]["draw_entropy_mean"] > 0
    def test_draw_entropy_current(self):
        r = compute_entropy_features(_d([[1,2,3,4,5],[6,7,8,9,10]]), (1,35))
        assert r["features"]["draw_entropy_current"] > 0
    def test_max_entropy(self):
        r = compute_entropy_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["features"]["max_entropy"] > 0
    def test_range_size(self):
        r = compute_entropy_features(_d([[1,2,3,4,5]]), (1,33))
        assert r["features"]["range_size"] == 33
