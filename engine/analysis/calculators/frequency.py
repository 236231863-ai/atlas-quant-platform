"""
Atlas Quant Platform - Frequency Analysis Engine.

Number frequency statistics and chi-square significance testing.
Pure computation: no IO, no database, no framework dependencies.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def frequency_analysis(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Analyze number frequency across all draws.

    Args:
        draws: List of draw records to analyze.
        main_range: (min, max) for main numbers.
        bonus_range: (min, max) for bonus numbers, if applicable.

    Returns:
        Dict with frequency statistics for main and bonus numbers.
    """
    if not draws:
        return {
            "analysis_type": "frequency",
            "total_draws": 0,
            "main_numbers": _empty_frequency(main_range),
            "bonus_numbers": _empty_frequency(bonus_range) if bonus_range else None,
        }

    # Count main number frequencies
    main_freq: Dict[int, int] = defaultdict(int)
    for draw in draws:
        for num in draw.main_numbers:
            main_freq[num] += 1

    main_result = _compute_frequency_stats(main_freq, draws, main_range, "main")

    # Count bonus number frequencies if applicable
    bonus_result = None
    if bonus_range:
        bonus_freq: Dict[int, int] = defaultdict(int)
        for draw in draws:
            if draw.bonus_numbers:
                for num in draw.bonus_numbers:
                    bonus_freq[num] += 1
        bonus_result = _compute_frequency_stats(bonus_freq, draws, bonus_range, "bonus")

    return {
        "analysis_type": "frequency",
        "total_draws": len(draws),
        "main_numbers": main_result,
        "bonus_numbers": bonus_result,
    }


def _empty_frequency(num_range: Tuple[int, int]) -> Dict[str, Any]:
    """Return empty frequency structure for a range."""
    min_v, max_v = num_range
    range_size = max_v - min_v + 1
    return {
        "range": {"min": min_v, "max": max_v, "size": range_size},
        "frequencies": {},
        "sorted_by_frequency": [],
        "total_occurrences": 0,
        "expected_per_number": 0.0,
        "chi_square": None,
    }


def _compute_frequency_stats(
    freq: Dict[int, int],
    draws: List[DrawRecordData],
    num_range: Tuple[int, int],
    label: str,
) -> Dict[str, Any]:
    """Compute frequency statistics for a set of numbers.

    Args:
        freq: Counter of number occurrences.
        draws: Full list of draw records.
        num_range: (min, max) for this number set.
        label: "main" or "bonus" for identification.

    Returns:
        Structured frequency statistics.
    """
    min_v, max_v = num_range
    range_size = max_v - min_v + 1

    # Total draws per number (each draw contributes count numbers)
    draws_per_number = len(draws)
    if label == "main":
        draws_per_number = len(draws) * 1  # each draw has main numbers
    else:
        draws_per_number = len(draws) * 1  # each draw has bonus numbers

    total_occurrences = sum(freq.values())
    expected = total_occurrences / range_size if range_size > 0 else 0

    # Build full frequency table
    frequencies: Dict[str, int] = {}
    observed: List[float] = []
    for n in range(min_v, max_v + 1):
        count = freq.get(n, 0)
        frequencies[str(n)] = count
        observed.append(float(count))

    expected_list = [expected] * range_size if expected > 0 else [0.0] * range_size

    # Perform chi-square test
    chi_square_result = None
    if expected > 0 and total_occurrences > 0:
        from scipy import stats as scipy_stats
        stat, p_value = scipy_stats.chisquare(observed, expected_list)
        chi_square_result = {
            "statistic": float(stat),
            "p_value": float(p_value),
            "significant": bool(p_value < 0.05),
            "degrees_of_freedom": range_size - 1,
        }

    # Sort by frequency descending
    sorted_by_freq = sorted(
        frequencies.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    # Top hot/cold numbers
    sorted_list = [(int(k), v) for k, v in sorted_by_freq]
    hot = sorted_list[:5] if len(sorted_list) >= 5 else sorted_list
    cold = sorted_list[-5:] if len(sorted_list) >= 5 else sorted_list
    cold = list(reversed(cold))

    return {
        "range": {"min": min_v, "max": max_v, "size": range_size},
        "frequencies": frequencies,
        "sorted_by_frequency": [(int(k), v) for k, v in sorted_by_freq],
        "total_occurrences": total_occurrences,
        "expected_per_number": round(expected, 2),
        "chi_square": chi_square_result,
        "hot_numbers": [{"number": n, "count": c} for n, c in hot],
        "cold_numbers": [{"number": n, "count": c} for n, c in cold],
        "frequency_rate": round(total_occurrences / draws_per_number, 4) if draws_per_number > 0 else 0,
    }
