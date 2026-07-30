"""Frequency features: occurrence rates, z-scores, expected deviations."""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def compute_frequency_features(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Compute frequency-based features for each number.

    Returns per-number features: occurrences, frequency_rate, z_score, deviation.
    """
    if not draws:
        return {"features": {}, "total_draws": 0, "feature_names": []}

    min_v, max_v = main_range
    range_size = max_v - min_v + 1
    total_numbers = len(draws) * 5  # DLT: 5 main numbers per draw
    expected = total_numbers / range_size if range_size > 0 else 0

    # Count occurrences
    counter: Counter[int] = Counter()
    for d in draws:
        counter.update(d.main_numbers)

    # Compute per-number features
    features: Dict[str, Dict[str, float]] = {}
    obs_list: List[float] = []
    for n in range(min_v, max_v + 1):
        count = counter.get(n, 0)
        freq_rate = count / len(draws) if draws else 0
        deviation = count - expected
        deviation_pct = (deviation / expected * 100) if expected > 0 else 0

        # Z-score approximation
        p = 5 / range_size  # probability of being drawn in one draw
        std = math.sqrt(len(draws) * p * (1 - p)) * 5 / range_size
        z_score = deviation / std if std > 0 else 0

        features[str(n)] = {
            "occurrences": count,
            "frequency_rate": round(freq_rate, 4),
            "expected": round(expected, 2),
            "deviation": round(deviation, 2),
            "deviation_pct": round(deviation_pct, 2),
            "z_score": round(z_score, 4),
        }
        obs_list.append(float(count))

    # Bonus numbers
    bonus_features = None
    if bonus_range:
        b_min, b_max = bonus_range
        b_counter: Counter[int] = Counter()
        for d in draws:
            if d.bonus_numbers:
                b_counter.update(d.bonus_numbers)
        bonus_features = {}
        for n in range(b_min, b_max + 1):
            bonus_features[str(n)] = {"occurrences": b_counter.get(n, 0)}

    # Overall statistics
    sorted_by_z = sorted(features.items(), key=lambda x: x[1]["z_score"], reverse=True)

    return {
        "features": features,
        "bonus_features": bonus_features,
        "total_draws": len(draws),
        "expected_per_number": round(expected, 2),
        "top_overrepresented": [{"number": k, "z_score": v["z_score"]} for k, v in sorted_by_z[:5]],
        "top_underrepresented": [{"number": k, "z_score": v["z_score"]} for k, v in sorted_by_z[-5:]],
        "feature_names": ["occurrences", "frequency_rate", "expected", "deviation", "deviation_pct", "z_score"],
    }
