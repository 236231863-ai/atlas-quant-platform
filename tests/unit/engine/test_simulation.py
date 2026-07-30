"""Tests for Monte Carlo Simulation and Expected Value engines."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.simulation import monte_carlo_simulation, expected_value_analysis


class TestMonteCarlo:
    def test_basic_simulation(self):
        result = monte_carlo_simulation(
            num_simulations=10, num_draws=5,
            main_range=(1, 35), main_count=5,
            random_seed=42,
        )
        assert result["num_simulations"] == 10
        assert result["num_draws_per_simulation"] == 5
        assert result["total_combinations_generated"] == 50

    def test_reproducible_with_seed(self):
        r1 = monte_carlo_simulation(5, 3, (1, 35), 5, random_seed=42)
        r2 = monte_carlo_simulation(5, 3, (1, 35), 5, random_seed=42)
        assert r1["main_numbers"]["frequencies"] == r2["main_numbers"]["frequencies"]

    def test_different_seeds_different_results(self):
        r1 = monte_carlo_simulation(5, 3, (1, 35), 5, random_seed=42)
        r2 = monte_carlo_simulation(5, 3, (1, 35), 5, random_seed=99)
        assert r1["main_numbers"]["frequencies"] != r2["main_numbers"]["frequencies"]

    def test_with_bonus_numbers(self):
        result = monte_carlo_simulation(
            10, 5, (1, 35), 5, (1, 12), 2, random_seed=42,
        )
        assert result["bonus_numbers"] is not None

    def test_total_occurrences(self):
        result = monte_carlo_simulation(
            10, 5, (1, 35), 5, random_seed=42,
        )
        # 10 sims * 5 draws * 5 numbers = 250
        assert result["main_numbers"]["total_occurrences"] == 250

    def test_chi_square_in_simulation(self):
        result = monte_carlo_simulation(
            100, 10, (1, 35), 5, random_seed=42,
        )
        assert result["main_numbers"]["chi_square"] is not None

    def test_entropy_in_simulation(self):
        result = monte_carlo_simulation(
            50, 10, (1, 35), 5, random_seed=42,
        )
        assert "entropy" in result["main_numbers"]

    def test_analysis_type(self):
        result = monte_carlo_simulation(5, 3, (1, 35), 5, random_seed=42)
        assert result["analysis_type"] == "monte_carlo"

    def test_range_small(self):
        result = monte_carlo_simulation(10, 5, (1, 5), 3, random_seed=42)
        assert result["main_numbers"]["range"]["size"] == 5


class TestExpectedValue:
    def test_basic_analysis(self):
        draws = [DrawRecordData(lottery_code="test", draw_number="1",
                                draw_date=date(2024, 1, 1), main_numbers=[1, 2, 3, 4, 5])]
        result = expected_value_analysis(draws, (1, 35), 5)
        assert result["total_draws"] == 1

    def test_empty_draws(self):
        result = expected_value_analysis([], (1, 35), 5)
        assert result["total_draws"] == 0

    def test_deviation_calculation(self):
        draws = [DrawRecordData(lottery_code="test", draw_number="1",
                                draw_date=date(2024, 1, 1), main_numbers=[1, 2, 3, 4, 5])]
        result = expected_value_analysis(draws, (1, 35), 5)
        assert result["numbers"]["1"]["actual"] == 1
        assert result["numbers"]["6"]["actual"] == 0
