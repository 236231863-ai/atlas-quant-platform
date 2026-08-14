"""
Atlas Quant Platform - Gap Analysis Engine.

Calculate current missing, average missing, and maximum missing
for each number across a sequence of draws.
Pure computation: no IO, no database.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData

DISCLAIMER = "统计分析仅陈述历史数据，不构成选号依据。开奖结果具有随机性。"


def gap_analysis(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Analyze number gaps (missing values) across draws.

    For each number, calculates:
    - Current gap: draws since the number last appeared
    - Average gap: mean gap between consecutive appearances
    - Maximum gap: longest gap between consecutive appearances
    - Minimum gap: shortest gap between consecutive appearances

    Args:
        draws: List of draw records (must be in chronological order).
        main_range: (min, max) for main numbers.
        bonus_range: (min, max) for bonus numbers.

    Returns:
        Dict with gap statistics.
    """
    if not draws:
        return _empty_gap_result(main_range, bonus_range)

    main_result = _compute_gap_stats(draws, main_range, "main")
    bonus_result = None
    if bonus_range:
        bonus_result = _compute_gap_stats(draws, bonus_range, "bonus")

    return {
        "analysis_type": "gap",
        "total_draws": len(draws),
        "main_numbers": main_result,
        "bonus_numbers": bonus_result,
        "disclaimer": DISCLAIMER,
    }


def _empty_gap_result(
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Return empty gap result structure."""
    def empty_range(r: Tuple[int, int]) -> Dict[str, Any]:
        min_v, max_v = r
        numbers = {str(n): {"current_gap": 0, "average_gap": 0.0, "max_gap": 0, "min_gap": 0, "appearances": 0} for n in range(min_v, max_v + 1)}
        return {
            "range": {"min": min_v, "max": max_v, "size": max_v - min_v + 1},
            "numbers": numbers,
            "current_max_gap": 0,
            "current_avg_gap": 0.0,
            "overall_max_gap": 0,
        }
    result = {
        "analysis_type": "gap",
        "total_draws": 0,
        "main_numbers": empty_range(main_range),
        "bonus_numbers": empty_range(bonus_range) if bonus_range else None,
        "disclaimer": DISCLAIMER,
    }
    return result


def _compute_gap_stats(
    draws: List[DrawRecordData],
    num_range: Tuple[int, int],
    label: str,
) -> Dict[str, Any]:
    """Compute gap statistics for a number range.

    Args:
        draws: Chronological list of draw records.
        num_range: (min, max) for this number set.
        label: "main" or "bonus".

    Returns:
        Gap statistics for this number range.
    """
    min_v, max_v = num_range
    range_size = max_v - min_v + 1

    # Track draw indices where each number appears
    number_draws: Dict[int, List[int]] = defaultdict(list)
    for idx, draw in enumerate(draws):
        numbers = draw.main_numbers if label == "main" else (draw.bonus_numbers or [])
        for num in numbers:
            if min_v <= num <= max_v:
                number_draws[num].append(idx)

    current_draw_idx = len(draws) - 1  # 0-based index of last draw

    numbers_data: Dict[str, Dict[str, Any]] = {}
    current_gaps: List[int] = []
    all_gaps: List[int] = []

    for num in range(min_v, max_v + 1):
        appearances = number_draws.get(num, [])

        if not appearances:
            # Number never appeared
            current_gap = current_draw_idx + 1  # all draws since the start
            numbers_data[str(num)] = {
                "current_gap": current_gap,
                "average_gap": float("inf"),
                "max_gap": current_gap,
                "min_gap": current_gap,
                "appearances": 0,
                "gaps": [current_gap],
            }
            current_gaps.append(current_gap)
            all_gaps.append(current_gap)
            continue

        # Calculate gaps between consecutive appearances
        gaps: List[int] = []
        prev_idx = -1
        for idx in appearances:
            gaps.append(idx - prev_idx - 1)
            prev_idx = idx

        # Current gap: draws since last appearance
        current_gap = current_draw_idx - appearances[-1]

        # Add current gap as the trailing gap
        gaps.append(current_gap)

        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)
        min_gap = min(gaps)

        numbers_data[str(num)] = {
            "current_gap": current_gap,
            "average_gap": round(avg_gap, 2),
            "max_gap": max_gap,
            "min_gap": min_gap,
            "appearances": len(appearances),
            "gaps": gaps,
        }
        current_gaps.append(current_gap)
        all_gaps.extend(gaps)

    # Overall statistics
    current_max = max(current_gaps) if current_gaps else 0
    current_avg = round(sum(current_gaps) / len(current_gaps), 2) if current_gaps else 0.0
    overall_max = max(all_gaps) if all_gaps else 0

    # Find top gaps (numbers with highest current gap)
    sorted_by_gap = sorted(
        numbers_data.items(),
        key=lambda x: x[1]["current_gap"],
        reverse=True,
    )

    return {
        "range": {"min": min_v, "max": max_v, "size": range_size},
        "numbers": numbers_data,
        "current_max_gap": current_max,
        "current_avg_gap": current_avg,
        "overall_max_gap": overall_max,
        "top_missing": [
            {"number": int(k), "current_gap": v["current_gap"],
             "average_gap": v["average_gap"], "max_gap": v["max_gap"]}
            for k, v in sorted_by_gap[:10]
        ],
    }
