"""Tests for Statistics Engine."""
from __future__ import annotations

import pytest
import math
from engine.statistics import (
    chi_square_test, normal_test, descriptive_stats,
    correlation_analysis, entropy_calculation, auto_correlation,
)


class TestChiSquare:
    def test_uniform_distribution(self):
        result = chi_square_test([10, 10, 10, 10])
        assert not result["significant"]

    def test_skewed_distribution(self):
        result = chi_square_test([30, 2, 2, 2])
        assert result["significant"]

    def test_chi_square_stat_positive(self):
        result = chi_square_test([10, 20, 5])
        assert result["chi_square_stat"] > 0

    def test_empty_expected_defaults_to_uniform(self):
        result = chi_square_test([5, 5, 5])
        assert result["p_value"] > 0.05


class TestNormalTest:
    def test_normal_data(self):
        data = [1, 2, 3, 4, 5] * 10
        result = normal_test(data)
        assert "is_normal" in result

    def test_insufficient_data(self):
        result = normal_test([1, 2])
        assert result["is_normal"]

    def test_constant_data(self):
        result = normal_test([1, 1, 1, 1, 1])
        assert "is_normal" in result


class TestDescriptiveStats:
    def test_empty_data(self):
        result = descriptive_stats([])
        assert result["count"] == 0

    def test_basic_stats(self):
        result = descriptive_stats([1, 2, 3, 4, 5])
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0

    def test_median_odd(self):
        result = descriptive_stats([1, 2, 3, 4, 5])
        assert result["median"] == 3.0

    def test_median_even(self):
        result = descriptive_stats([1, 2, 3, 4])
        assert result["median"] == 2.5

    def test_skewness(self):
        result = descriptive_stats([1, 1, 1, 2, 10])
        assert "skewness" in result


class TestCorrelation:
    def test_perfect_positive(self):
        result = correlation_analysis([1, 2, 3], [2, 4, 6])
        assert result["coefficient"] == pytest.approx(1.0, abs=0.01)

    def test_perfect_negative(self):
        result = correlation_analysis([1, 2, 3], [3, 2, 1])
        assert result["coefficient"] == pytest.approx(-1.0, abs=0.01)

    def test_no_correlation(self):
        result = correlation_analysis([1, 2, 3], [3, 1, 2])
        assert result["coefficient"] is not None

    def test_insufficient_data(self):
        result = correlation_analysis([1], [2])
        assert result["coefficient"] == 0.0

    def test_spearman_method(self):
        result = correlation_analysis([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], "spearman")
        assert result["method"] == "spearman"

    def test_strength_label(self):
        result = correlation_analysis([1, 2, 3], [2, 4, 6])
        assert result["strength"] == "very_strong"


class TestEntropy:
    def test_uniform_distribution(self):
        data = [1, 2, 3, 4] * 25
        result = entropy_calculation(data, (1, 4))
        assert result["normalized_entropy"] == pytest.approx(1.0, abs=0.01)

    def test_skewed_distribution(self):
        data = [1] * 90 + [2] * 10
        result = entropy_calculation(data, (1, 4))
        assert result["normalized_entropy"] < 0.5

    def test_empty_data(self):
        result = entropy_calculation([], (1, 10))
        assert result["shannon_entropy"] == 0.0

    def test_uniformity_pct(self):
        data = [1, 2, 3, 4] * 25
        result = entropy_calculation(data, (1, 4))
        assert result["uniformity_percentage"] > 90

    def test_single_value(self):
        data = [1] * 100
        result = entropy_calculation(data, (1, 10))
        assert result["shannon_entropy"] == 0.0


class TestAutoCorrelation:
    def test_lag_one(self):
        data = [1, 2, 3, 4, 5] * 5
        result = auto_correlation(data, 1)
        assert "coefficient" in result

    def test_lag_two(self):
        data = [1, 2, 3, 4, 5] * 5
        result = auto_correlation(data, 2)
        assert result["lag"] == 2

    def test_insufficient_data(self):
        result = auto_correlation([1, 2], 3)
        assert result["coefficient"] == 0.0
