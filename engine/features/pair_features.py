"""Pair features: co-occurrence frequency of number pairs."""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def compute_pair_features(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    top_n: int = 20,
) -> Dict[str, Any]:
    """Compute pair occurrence features.

    Analyzes which number pairs appear together most/least frequently.
    """
    if not draws:
        return {"features": {}, "total_draws": 0, "feature_names": []}

    min_v, max_v = main_range

    # Count pair occurrences
    pair_counter: Counter[Tuple[int, ...]] = Counter()
    for d in draws:
        nums = sorted(d.main_numbers)
        for pair in combinations(nums, 2):
            pair_counter[pair] += 1

    total_pairs = sum(pair_counter.values())
    expected_per_pair = total_pairs / (max_v - min_v + 1) if (max_v - min_v) > 0 else 0

    # Top pairs
    top_pairs = pair_counter.most_common(top_n)
    # Bottom pairs (least frequent)
    bottom_pairs = pair_counter.most_common()[-top_n:] if len(pair_counter) >= top_n else pair_counter.most_common()

    # Per-number pair frequency (how often each number appears in pairs)
    number_pair_count: Dict[int, int] = {}
    for (a, b), count in pair_counter.items():
        number_pair_count[a] = number_pair_count.get(a, 0) + count
        number_pair_count[b] = number_pair_count.get(b, 0) + count

    # Normalized pair strength
    sorted_by_strength = sorted(number_pair_count.items(), key=lambda x: x[1], reverse=True)

    features: Dict[str, Any] = {
        "total_pairs_analyzed": total_pairs,
        "unique_pairs_found": len(pair_counter),
        "expected_per_pair": round(expected_per_pair, 2),
        "top_10_pairs": [{"pair": list(p), "count": c} for p, c in top_pairs[:10]],
        "bottom_10_pairs": [{"pair": list(p), "count": c} for p, c in bottom_pairs[:10]],
        "most_connected_numbers": [{"number": n, "pair_count": c} for n, c in sorted_by_strength[:10]],
        "current_draw_pairs": [],
    }

    # Current draw pairs
    if draws:
        last_draw = draws[-1]
        current_pairs = list(combinations(sorted(last_draw.main_numbers), 2))
        features["current_draw_pairs"] = [
            {"pair": list(p), "historical_count": pair_counter.get(p, 0)}
            for p in current_pairs
        ]

    return {
        "features": features,
        "total_draws": len(draws),
        "feature_names": ["total_pairs_analyzed", "unique_pairs_found", "expected_per_pair",
                          "top_10_pairs", "bottom_10_pairs", "most_connected_numbers"],
    }
