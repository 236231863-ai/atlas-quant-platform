"""Tests for gap feature computation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.features.gap_features import compute_gap_features

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

D = _d([[1,2,3,4,5],[6,7,8,9,10],[1,2,3,4,5],[6,7,8,9,10]])

class TestGapFeatures:
    def test_empty(self):
        r = compute_gap_features([], (1,35))
        assert r["total_draws"] == 0
    def test_current_gap_just_appeared(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["6"]["current_gap"] == 0
    def test_current_gap_never_appeared(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["35"]["current_gap"] == 4
    def test_appearances_count(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["1"]["appearances"] == 2
    def test_avg_gap_computed(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["1"]["avg_gap"] > 0
    def test_max_gap_computed(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["1"]["max_gap"] >= 0
    def test_gap_ratio(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["1"]["gap_ratio"] >= 0
    def test_current_max_gap(self):
        r = compute_gap_features(D, (1,35))
        assert r["current_max_gap"] > 0
    def test_current_avg_gap(self):
        r = compute_gap_features(D, (1,35))
        assert r["current_avg_gap"] > 0
    def test_top_missing(self):
        r = compute_gap_features(D, (1,35))
        assert len(r["top_missing"]) == 10
    def test_single_draw(self):
        r = compute_gap_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["total_draws"] == 1
    def test_feature_names(self):
        r = compute_gap_features(D, (1,35))
        assert "gap_ratio" in r["feature_names"]
    def test_gap_ratio_one_for_never_appeared(self):
        r = compute_gap_features(D, (1,35))
        assert r["features"]["35"]["gap_ratio"] == 1.0
    def test_all_numbers_present(self):
        r = compute_gap_features(D, (1,10))
        for n in range(1,11):
            assert str(n) in r["features"]
