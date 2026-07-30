"""Gap features: current gap, avg gap, max gap, gap ratio."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def compute_gap_features(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Compute gap-based features for each number.

    Returns per-number features: current_gap, avg_gap, max_gap, min_gap, gap_ratio.
    """
    if not draws:
        return {"features": {}, "total_draws": 0, "feature_names": []}

    min_v, max_v = main_range
    # Track draw indices where each number appears
    number_draws: Dict[int, List[int]] = defaultdict(list)
    for idx, d in enumerate(draws):
        for n in d.main_numbers:
            if min_v <= n <= max_v:
                number_draws[n].append(idx)

    current_idx = len(draws) - 1
    features: Dict[str, Dict[str, Any]] = {}
    gap_list: List[float] = []

    for n in range(min_v, max_v + 1):
        appearances = number_draws.get(n, [])
        if not appearances:
            current_gap = current_idx + 1
            features[str(n)] = {
                "current_gap": current_gap, "avg_gap": current_gap,
                "max_gap": current_gap, "min_gap": current_gap,
                "appearances": 0, "gap_ratio": 1.0,
            }
            gap_list.append(float(current_gap))
            continue

        gaps: List[int] = []
        prev = -1
        for a in appearances:
            gaps.append(a - prev - 1)
            prev = a
        gaps.append(current_idx - appearances[-1])

        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)
        min_gap = min(gaps)
        current_gap = gaps[-1]
        gap_ratio = current_gap / avg_gap if avg_gap > 0 else 1.0

        features[str(n)] = {
            "current_gap": current_gap, "avg_gap": round(avg_gap, 2),
            "max_gap": max_gap, "min_gap": min_gap,
            "appearances": len(appearances), "gap_ratio": round(gap_ratio, 4),
        }
        gap_list.append(float(current_gap))

    sorted_by_gap = sorted(features.items(), key=lambda x: x[1]["current_gap"], reverse=True)

    return {
        "features": features,
        "total_draws": len(draws),
        "current_max_gap": max(gap_list) if gap_list else 0,
        "current_avg_gap": round(sum(gap_list) / len(gap_list), 2) if gap_list else 0,
        "top_missing": [{"number": k, "current_gap": v["current_gap"]} for k, v in sorted_by_gap[:10]],
        "feature_names": ["current_gap", "avg_gap", "max_gap", "min_gap", "appearances", "gap_ratio"],
    }
