"""Tests for Report Generator."""
from __future__ import annotations

import pytest
from engine.report import ReportGenerator


class TestReportGenerator:
    def setup_method(self):
        self.gen = ReportGenerator()

    def test_empty_frequency_report(self):
        result = self.gen.generate_markdown({
            "analysis_type": "frequency",
            "total_draws": 0,
            "main_numbers": {
                "range": {"min": 1, "max": 33, "size": 33},
                "frequencies": {},
                "total_occurrences": 0,
                "expected_per_number": 0,
            },
        })
        assert "Frequency" in result
        assert "0" in result

    def test_frequency_report_with_data(self):
        result = self.gen.generate_markdown({
            "analysis_type": "frequency",
            "total_draws": 10,
            "main_numbers": {
                "range": {"min": 1, "max": 33, "size": 33},
                "frequencies": {"1": 5, "2": 3},
                "total_occurrences": 60,
                "expected_per_number": 1.82,
                "hot_numbers": [{"number": 1, "count": 5}],
                "cold_numbers": [{"number": 33, "count": 0}],
                "chi_square": {"statistic": 15.3, "p_value": 0.05, "significant": False},
                "sorted_by_frequency": [(1, 5), (2, 3)],
            },
        })
        assert "## Main Numbers" in result
        assert "**1**" in result
        assert "Chi-Square" in result

    def test_gap_report(self):
        result = self.gen.generate_markdown({
            "analysis_type": "gap",
            "total_draws": 10,
            "main_numbers": {
                "range": {"min": 1, "max": 35, "size": 35},
                "current_max_gap": 8,
                "current_avg_gap": 3.5,
                "overall_max_gap": 12,
                "top_missing": [
                    {"number": 35, "current_gap": 8, "average_gap": 4.0, "max_gap": 8},
                ],
                "numbers": {},
            },
        })
        assert "Current Max Gap" in result
        assert "Top Missing" in result

    def test_distribution_report(self):
        result = self.gen.generate_markdown({
            "analysis_type": "distribution",
            "total_draws": 5,
            "odd_even": {"distribution": {"3:3": 3, "4:2": 2}, "percentages": {"3:3": 60}, "current": "3:3"},
            "high_low": {"distribution": {"2:4": 5}, "percentages": {"2:4": 100}, "midpoint": 17},
            "sum_values": {"current": 100, "mean": 95, "median": 90, "min": 70, "max": 120, "std": 15},
            "span_values": {"current": 28, "mean": 25, "median": 24, "min": 10, "max": 32},
        })
        assert "Odd/Even" in result
        assert "High/Low" in result
        assert "Sum Distribution" in result
        assert "Span Distribution" in result

    def test_monte_carlo_report(self):
        result = self.gen.generate_markdown({
            "analysis_type": "monte_carlo",
            "num_simulations": 100,
            "num_draws_per_simulation": 10,
            "total_combinations_generated": 1000,
            "main_numbers": {
                "range": {"min": 1, "max": 35, "size": 35},
                "entropy": {"shannon_entropy": 5.12, "normalized_entropy": 0.98, "uniformity_pct": 98.0},
            },
        })
        assert "Monte Carlo" in result
        assert "100 simulations" in result
        assert "Uniformity" in result

    def test_report_has_disclaimer(self):
        result = self.gen.generate_markdown({
            "analysis_type": "frequency", "total_draws": 0,
            "main_numbers": {"range": {"min": 1, "max": 33, "size": 33},
                             "frequencies": {}, "total_occurrences": 0, "expected_per_number": 0},
        })
        assert "academic research" in result.lower()
        assert "Does not predict" in result

    def test_report_title_customizable(self):
        self.gen.set_title("Custom Report")
        result = self.gen.generate_markdown({
            "analysis_type": "frequency", "total_draws": 0,
            "main_numbers": {"range": {"min": 1, "max": 33, "size": 33},
                             "frequencies": {}, "total_occurrences": 0, "expected_per_number": 0},
        })
        assert "Custom Report" in result

    def test_generate_json(self):
        result = self.gen.generate_json({"key": "value", "nested": {"a": 1}})
        assert '"key": "value"' in result
        assert '"a": 1' in result

    def test_generate_csv(self):
        data = [{"col_a": 1, "col_b": "x"}, {"col_a": 2, "col_b": "y"}]
        result = self.gen.generate_csv(data)
        assert "col_a" in result
        assert "col_b" in result
