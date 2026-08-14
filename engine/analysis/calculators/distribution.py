"""
Atlas Quant Platform - Distribution Analysis Engine.

Analyze number distributions: odd/even, high/low, zones, sum, span.
Pure computation: no IO, no database.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData

DISCLAIMER = "统计分析仅陈述历史数据，不构成选号依据。开奖结果具有随机性。"


def distribution_analysis(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
) -> Dict[str, Any]:
    """Analyze number distributions across draws.

    Calculates:
    - Odd/even ratio distribution
    - High/low ratio distribution (high > midpoint of range)
    - Zone distribution (divides range into 3 zones)
    - Sum value distribution
    - Span distribution (max - min)

    Args:
        draws: List of draw records.
        main_range: (min, max) for main numbers.

    Returns:
        Dict with all distribution analyses.
    """
    if not draws:
        return {
            "analysis_type": "distribution",
            "total_draws": 0,
            "odd_even": {},
            "high_low": {},
            "zone_distribution": {},
            "sum_values": {},
            "span_values": {},
            "disclaimer": DISCLAIMER,
        }

    min_v, max_v = main_range
    midpoint = (min_v + max_v) / 2
    zone_size = (max_v - min_v + 1) / 3

    odd_even_counter: Counter[str] = Counter()
    high_low_counter: Counter[str] = Counter()
    zone_counters: List[Counter[str]] = [Counter(), Counter(), Counter()]
    sums: List[int] = []
    spans: List[int] = []

    # Track current draw for reference
    latest_sum = 0
    latest_span = 0
    latest_odd_even = ""
    latest_high_low = ""

    for draw in draws:
        numbers = draw.main_numbers
        n = len(numbers)

        # Odd/Even
        odd_count = sum(1 for x in numbers if x % 2 == 1)
        even_count = n - odd_count
        key_oe = f"{odd_count}:{even_count}"
        odd_even_counter[key_oe] += 1
        latest_odd_even = key_oe

        # High/Low
        high_count = sum(1 for x in numbers if x > midpoint)
        low_count = n - high_count
        key_hl = f"{high_count}:{low_count}"
        high_low_counter[key_hl] += 1
        latest_high_low = key_hl

        # Zone distribution (1/3 splits)
        for num in numbers:
            zone_idx = min(2, int((num - min_v) / zone_size)) if zone_size > 0 else 0
            zone_counters[zone_idx][str(num)] += 1

        # Sum
        draw_sum = sum(numbers)
        sums.append(draw_sum)
        latest_sum = draw_sum

        # Span
        draw_span = max(numbers) - min(numbers)
        spans.append(draw_span)
        latest_span = draw_span

    # Odd/Even summary
    oe_total = sum(odd_even_counter.values())
    odd_even_result = {
        "distribution": dict(odd_even_counter.most_common()),
        "percentages": {
            k: round(v / oe_total * 100, 1) for k, v in odd_even_counter.most_common()
        },
        "current": latest_odd_even,
        "most_common": odd_even_counter.most_common(1)[0][0] if odd_even_counter else "",
    }

    # High/Low summary
    hl_total = sum(high_low_counter.values())
    high_low_result = {
        "distribution": dict(high_low_counter.most_common()),
        "percentages": {
            k: round(v / hl_total * 100, 1) for k, v in high_low_counter.most_common()
        },
        "current": latest_high_low,
        "midpoint": midpoint,
        "most_common": high_low_counter.most_common(1)[0][0] if high_low_counter else "",
    }

    # Zone summary
    zone_names = ["low", "medium", "high"]
    zone_result = {}
    for i, zone_cnt in enumerate(zone_counters):
        z_total = sum(zone_cnt.values())
        zone_result[zone_names[i]] = {
            "range": {
                "min": int(min_v + i * zone_size),
                "max": int(min_v + (i + 1) * zone_size - 1),
            },
            "total_appearances": z_total,
            "numbers": dict(zone_cnt.most_common(10)),
        }

    # Sum statistics
    sum_result = _compute_numeric_stats(sums)
    sum_result["current"] = latest_sum

    # Span statistics
    span_result = _compute_numeric_stats(spans)
    span_result["current"] = latest_span

    return {
        "analysis_type": "distribution",
        "total_draws": len(draws),
        "odd_even": odd_even_result,
        "high_low": high_low_result,
        "zone_distribution": zone_result,
        "sum_values": sum_result,
        "span_values": span_result,
        "disclaimer": DISCLAIMER,
    }


def _compute_numeric_stats(values: List[int]) -> Dict[str, Any]:
    """Compute statistics for a list of numeric values."""
    if not values:
        return {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0}

    arr = sorted(values)
    n = len(arr)
    mean = sum(arr) / n
    variance = sum((x - mean) ** 2 for x in arr) / n
    std = variance ** 0.5

    return {
        "mean": round(mean, 2),
        "median": float(arr[n // 2]) if n % 2 == 1 else float((arr[n // 2 - 1] + arr[n // 2]) / 2),
        "min": min(arr),
        "max": max(arr),
        "std": round(std, 2),
        "range": max(arr) - min(arr),
        "recent_10": values[-10:] if len(values) >= 10 else values,
    }
