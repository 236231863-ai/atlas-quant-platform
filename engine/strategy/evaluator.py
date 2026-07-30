"""
Atlas Quant Platform - Strategy Evaluator.

Executes strategy rules against historical draw data to select numbers.
Each strategy is JSON data, not code. Pure computation, no IO.
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


class StrategyEvaluator:
    """Evaluates a strategy against historical data to select numbers.

    Supports strategy types:
    - gap_based: Select numbers with highest current gap
    - frequency_based: Select most/least frequent numbers
    - fixed: Always select same numbers
    - random: Random selection
    - mixed: Combination of strategies
    """

    def evaluate(
        self,
        history: List[DrawRecordData],
        main_range: Tuple[int, int],
        main_count: int,
        bonus_range: Optional[Tuple[int, int]] = None,
        bonus_count: int = 0,
        strategy_type: str = "gap_based",
        strategy_params: Optional[Dict[str, Any]] = None,
        rng: Optional[random.Random] = None,
    ) -> Tuple[List[int], Optional[List[int]]]:
        """Select numbers based on strategy and historical data.

        Args:
            history: Draw records BEFORE the current draw (no future data).
            main_range: (min, max) for main numbers.
            main_count: How many main numbers to select.
            bonus_range: (min, max) for bonus numbers.
            bonus_count: How many bonus numbers to select.
            strategy_type: Type of strategy to use.
            strategy_params: Parameters for the strategy.
            rng: Random number generator (seeded for reproducibility).

        Returns:
            Tuple of (selected_main_numbers, selected_bonus_numbers_or_None).
        """
        if rng is None:
            rng = random.Random()
        params = strategy_params or {}

        main_min, main_max = main_range
        bonus_min = bonus_min_orig = 0
        bonus_max = 0
        if bonus_range:
            bonus_min, bonus_max = bonus_range

        # Select main numbers
        main_selected = self._select_numbers(
            history, main_range, main_count, strategy_type, params, rng, is_bonus=False
        )

        # Select bonus numbers
        bonus_selected = None
        if bonus_range and bonus_count > 0:
            bonus_selected = self._select_numbers(
                history, bonus_range, bonus_count, strategy_type, params, rng, is_bonus=True
            )

        return main_selected, bonus_selected

    def _select_numbers(
        self,
        history: List[DrawRecordData],
        num_range: Tuple[int, int],
        count: int,
        strategy_type: str,
        params: Dict[str, Any],
        rng: random.Random,
        is_bonus: bool = False,
    ) -> List[int]:
        """Select numbers based on strategy type."""
        min_v, max_v = num_range
        all_numbers = list(range(min_v, max_v + 1))
        field = "bonus_numbers" if is_bonus else "main_numbers"

        # Filter available numbers based on strategy type
        if strategy_type == "gap_based":
            min_gap = params.get("min_gap", 5)
            candidates = self._filter_by_gap(history, all_numbers, field, min_gap)
            # Sort by gap descending, take top N
            candidates.sort(key=lambda x: x[1], reverse=True)
            selected = [n for n, _ in candidates[:count]]
            # Fill remaining if not enough
            if len(selected) < count:
                remaining = [n for n in all_numbers if n not in selected]
                rng.shuffle(remaining)
                selected.extend(remaining[:count - len(selected)])

        elif strategy_type == "hot":
            candidates = self._filter_by_frequency(history, all_numbers, field)
            candidates.sort(key=lambda x: x[1], reverse=True)
            selected = [n for n, _ in candidates[:count]]

        elif strategy_type == "cold":
            candidates = self._filter_by_frequency(history, all_numbers, field)
            candidates.sort(key=lambda x: x[1])
            selected = [n for n, _ in candidates[:count]]

        elif strategy_type == "fixed":
            fixed = params.get("numbers", [])
            selected = [n for n in fixed if min_v <= n <= max_v][:count]
            if len(selected) < count:
                remaining = [n for n in all_numbers if n not in selected]
                rng.shuffle(remaining)
                selected.extend(remaining[:count - len(selected)])

        elif strategy_type == "even":
            evens = [n for n in all_numbers if n % 2 == 0]
            rng.shuffle(evens)
            selected = sorted(evens[:count])

        elif strategy_type == "odd":
            odds = [n for n in all_numbers if n % 2 == 1]
            rng.shuffle(odds)
            selected = sorted(odds[:count])

        else:  # random
            selected = sorted(rng.sample(all_numbers, min(count, len(all_numbers))))

        return sorted(selected)[:count]

    def _filter_by_gap(
        self,
        history: List[DrawRecordData],
        all_numbers: List[int],
        field: str,
        min_gap: int,
    ) -> List[Tuple[int, int]]:
        """Filter numbers by minimum gap from last appearance."""
        if not history:
            return [(n, min_gap) for n in all_numbers]

        last_seen: Dict[int, int] = {}
        for i, draw in enumerate(reversed(history)):
            nums = getattr(draw, field, []) or []
            for n in nums:
                if n not in last_seen:
                    last_seen[n] = i + 1

        result = []
        for n in all_numbers:
            gap = last_seen.get(n, len(history) + 1)
            if gap >= min_gap:
                result.append((n, gap))
        return result

    def _filter_by_frequency(
        self,
        history: List[DrawRecordData],
        all_numbers: List[int],
        field: str,
    ) -> List[Tuple[int, int]]:
        """Count frequency of each number in history."""
        counter: Dict[int, int] = {n: 0 for n in all_numbers}
        for draw in history:
            nums = getattr(draw, field, []) or []
            for n in nums:
                if n in counter:
                    counter[n] += 1
        return list(counter.items())
