"""Distribution features: odd/even, high/low, sum, span, zone."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def compute_distribution_features(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
) -> Dict[str, Any]:
    """Compute distribution-based features.

    Returns odd/even ratio, high/low ratio, zone distribution,
    sum stats, span stats as numeric features.
    """
    if not draws:
        return {"features": {}, "total_draws": 0, "feature_names": []}

    min_v, max_v = main_range
    midpoint = (min_v + max_v) / 2
    zone_size = (max_v - min_v + 1) / 3

    sums: List[int] = []
    spans: List[int] = []
    odd_counts: List[int] = []
    high_counts: List[int] = []
    zone_counts = [0, 0, 0]

    for d in draws:
        nums = d.main_numbers
        n = len(nums)
        odd_counts.append(sum(1 for x in nums if x % 2 == 1))
        high_counts.append(sum(1 for x in nums if x > midpoint))
        sums.append(sum(nums))
        spans.append(max(nums) - min(nums))
        for x in nums:
            zi = min(2, int((x - min_v) / zone_size)) if zone_size > 0 else 0
            zone_counts[zi] += 1

    features: Dict[str, Any] = {}
    # Odd/Even features
    odd_pcts = [o / n * 100 for o, n in zip(odd_counts, [len(d.main_numbers) for d in draws])]
    features["odd_even_ratio_avg"] = round(sum(odd_pcts) / len(odd_pcts), 2) if odd_pcts else 0
    features["odd_even_ratio_current"] = round(odd_pcts[-1], 2) if odd_pcts else 0
    features["odd_even_ratio_std"] = _std(odd_pcts)

    # High/Low features
    hl_pcts = [h / n * 100 for h, n in zip(high_counts, [len(d.main_numbers) for d in draws])]
    features["high_low_ratio_avg"] = round(sum(hl_pcts) / len(hl_pcts), 2) if hl_pcts else 0
    features["high_low_ratio_current"] = round(hl_pcts[-1], 2) if hl_pcts else 0

    # Zone features
    total_zone = sum(zone_counts) or 1
    features["zone_low_pct"] = round(zone_counts[0] / total_zone * 100, 2)
    features["zone_mid_pct"] = round(zone_counts[1] / total_zone * 100, 2)
    features["zone_high_pct"] = round(zone_counts[2] / total_zone * 100, 2)

    # Sum features
    features["sum_mean"] = round(sum(sums) / len(sums), 2) if sums else 0
    features["sum_std"] = round(_std(sums), 2)
    features["sum_current"] = sums[-1] if sums else 0
    features["sum_min"] = min(sums) if sums else 0
    features["sum_max"] = max(sums) if sums else 0

    # Span features
    features["span_mean"] = round(sum(spans) / len(spans), 2) if spans else 0
    features["span_std"] = round(_std(spans), 2)
    features["span_current"] = spans[-1] if spans else 0
    features["span_min"] = min(spans) if spans else 0
    features["span_max"] = max(spans) if spans else 0

    return {
        "features": features,
        "total_draws": len(draws),
        "feature_names": list(features.keys()),
    }


def _std(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = sum(vals) / len(vals)
    return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5
