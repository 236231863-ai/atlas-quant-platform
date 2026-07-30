"""Tests for distribution feature computation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.features.distribution_features import compute_distribution_features

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

D = _d([[1,3,5,7,9,11],[2,4,6,8,10,12],[1,2,3,4,5,6],[7,8,9,10,11,12]])

class TestDistributionFeatures:
    def test_empty(self):
        r = compute_distribution_features([], (1,33))
        assert r["total_draws"] == 0
    def test_odd_even_ratio(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["odd_even_ratio_avg"] > 0
    def test_odd_even_current(self):
        r = compute_distribution_features(D, (1,33))
        assert "odd_even_ratio_current" in r["features"]
    def test_high_low_avg(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["high_low_ratio_avg"] >= 0
    def test_zone_low_pct(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["zone_low_pct"] > 0
    def test_zone_high_pct(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["zone_high_pct"] > 0
    def test_sum_mean(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["sum_mean"] > 0
    def test_sum_current(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["sum_current"] > 0
    def test_span_mean(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["span_mean"] > 0
    def test_span_current(self):
        r = compute_distribution_features(D, (1,33))
        assert r["features"]["span_current"] > 0
    def test_feature_names(self):
        r = compute_distribution_features(D, (1,33))
        assert len(r["feature_names"]) > 5
    def test_single_draw(self):
        r = compute_distribution_features(_d([[1,2,3,4,5]]), (1,33))
        assert r["total_draws"] == 1
