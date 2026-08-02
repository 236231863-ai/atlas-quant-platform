"""Tests for frequency feature computation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.features.frequency_features import compute_frequency_features

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

D = _d([[1,2,3,4,5],[1,2,3,6,7],[1,2,8,9,10],[11,12,13,14,15]])

class TestFrequencyFeatures:
    def test_empty_draws(self):
        r = compute_frequency_features([], (1,35))
        assert r["total_draws"] == 0
    def test_occurrences_counted(self):
        r = compute_frequency_features(D, (1,35))
        assert r["features"]["1"]["occurrences"] == 3
    def test_zero_occurrences(self):
        r = compute_frequency_features(D, (1,35))
        assert r["features"]["35"]["occurrences"] == 0
    def test_frequency_rate(self):
        r = compute_frequency_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["features"]["1"]["frequency_rate"] > 0
    def test_expected_per_number(self):
        r = compute_frequency_features(D, (1,35))
        assert r["expected_per_number"] > 0
    def test_z_score_computed(self):
        r = compute_frequency_features(D, (1,35))
        assert "z_score" in r["features"]["1"]
    def test_z_score_positive_for_frequent(self):
        r = compute_frequency_features(D, (1,35))
        assert r["features"]["1"]["z_score"] > r["features"]["35"]["z_score"]
    def test_deviation_pct(self):
        r = compute_frequency_features(D, (1,35))
        assert "deviation_pct" in r["features"]["1"]
    def test_top_overrepresented(self):
        r = compute_frequency_features(D, (1,35))
        assert len(r["top_overrepresented"]) == 5
    def test_top_underrepresented(self):
        r = compute_frequency_features(D, (1,35))
        assert len(r["top_underrepresented"]) == 5
    def test_feature_names_present(self):
        r = compute_frequency_features(D, (1,35))
        assert "z_score" in r["feature_names"]
    def test_single_draw(self):
        r = compute_frequency_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["total_draws"] == 1
    def test_bonus_features_none(self):
        r = compute_frequency_features(D, (1,35))
        assert r["bonus_features"] is None
    def test_bonus_features_with(self):
        r = compute_frequency_features(D, (1,35), (1,12))
        assert r["bonus_features"] is not None
    def test_all_numbers_in_range(self):
        r = compute_frequency_features(D, (1,35))
        for n in range(1,36):
            assert str(n) in r["features"]
