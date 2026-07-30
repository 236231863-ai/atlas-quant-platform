"""Entropy features: Shannon entropy, uniformity, information measures."""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData


def compute_entropy_features(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
) -> Dict[str, Any]:
    """Compute entropy-based features.

    Shannon entropy measures the uniformity of number distribution.
    Higher entropy = more uniform.
    """
    if not draws:
        return {"features": {}, "total_draws": 0, "feature_names": []}

    min_v, max_v = main_range
    range_size = max_v - min_v + 1

    # Count per-number frequency
    counter: Counter[int] = Counter()
    for d in draws:
        counter.update(d.main_numbers)
    total = sum(counter.values())

    # Shannon entropy for overall distribution
    entropy = 0.0
    for n in range(min_v, max_v + 1):
        p = counter.get(n, 0) / total if total > 0 else 0
        if p > 0:
            entropy -= p * math.log2(p)

    max_entropy = math.log2(range_size)
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Per-draw entropy (how spread out each individual draw is)
    draw_entropies: List[float] = []
    for d in draws:
        de = 0.0
        for n in d.main_numbers:
            p = 1 / len(d.main_numbers)
            de -= p * math.log2(p)
        draw_entropies.append(round(de, 4))

    # Evenness (Pielou: J = H / Hmax)
    evenness = normalized_entropy

    features: Dict[str, Any] = {
        "shannon_entropy": round(entropy, 4),
        "max_entropy": round(max_entropy, 4),
        "normalized_entropy": round(normalized_entropy, 4),
        "evenness": round(evenness, 4),
        "uniformity_pct": round(normalized_entropy * 100, 2),
        "range_size": range_size,
        "total_observations": total,
        "draw_entropy_mean": round(sum(draw_entropies) / len(draw_entropies), 4) if draw_entropies else 0,
        "draw_entropy_current": draw_entropies[-1] if draw_entropies else 0,
    }

    return {
        "features": features,
        "total_draws": len(draws),
        "feature_names": list(features.keys()),
    }
