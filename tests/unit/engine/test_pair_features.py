"""Tests for pair feature computation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.features.pair_features import compute_pair_features

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

D = _d([[1,2,3,4,5],[1,2,3,4,6],[1,2,3,4,7],[8,9,10,11,12]])

class TestPairFeatures:
    def test_empty(self):
        r = compute_pair_features([], (1,35))
        assert r["total_draws"] == 0
    def test_total_pairs(self):
        r = compute_pair_features(D, (1,35))
        assert r["features"]["total_pairs_analyzed"] > 0
    def test_unique_pairs(self):
        r = compute_pair_features(D, (1,35))
        assert r["features"]["unique_pairs_found"] > 0
    def test_top_pairs_most_common(self):
        r = compute_pair_features(D, (1,35))
        assert r["features"]["top_10_pairs"][0]["pair"] == [1, 2]
    def test_top_pairs_limit(self):
        r = compute_pair_features(D, (1,35), top_n=5)
        assert len(r["features"]["top_10_pairs"]) == 5
    def test_most_connected(self):
        r = compute_pair_features(D, (1,35))
        assert r["features"]["most_connected_numbers"][0]["number"] == 1
    def test_current_draw_pairs(self):
        r = compute_pair_features(D, (1,35))
        assert len(r["features"]["current_draw_pairs"]) == 10  # C(5,2)
    def test_expected_per_pair(self):
        r = compute_pair_features(D, (1,35))
        assert r["features"]["expected_per_pair"] > 0
    def test_single_draw(self):
        r = compute_pair_features(_d([[1,2,3,4,5]]), (1,35))
        assert r["total_draws"] == 1
    def test_feature_names(self):
        r = compute_pair_features(D, (1,35))
        assert "top_10_pairs" in r["feature_names"]
    def test_all_draws_have_pairs(self):
        r = compute_pair_features(_d([[1,2,3,4,5],[6,7,8,9,10]]), (1,35))
        assert r["features"]["total_pairs_analyzed"] == 20  # 10 pairs per draw * 2 draws
