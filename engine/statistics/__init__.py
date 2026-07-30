"""
Atlas Quant Platform - Statistics Engine.

统计引擎提供假设检验、分布拟合、相关性分析、熵计算等统计方法。
所有函数为纯计算，无副作用。
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats as scipy_stats

from engine import EngineResult


def chi_square_test(
    observed: List[float],
    expected: Optional[List[float]] = None,
) -> EngineResult:
    """卡方检验 - 检验观察频率与期望频率的差异。"""
    if expected is None:
        expected = [sum(observed) / len(observed)] * len(observed)

    stat, p_value = scipy_stats.chisquare(observed, expected)
    return {
        "chi_square_stat": float(stat),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
    }


def normal_test(data: List[float]) -> EngineResult:
    """正态性检验 (D'Agostino-Pearson)。"""
    if len(data) < 3:
        return {"statistic": 0.0, "p_value": 1.0, "is_normal": True, "note": "Insufficient data"}
    stat, p_value = scipy_stats.normaltest(data)
    return {
        "statistic": float(stat),
        "p_value": float(p_value),
        "is_normal": p_value >= 0.05,
    }


def descriptive_stats(data: List[float]) -> EngineResult:
    """描述性统计。"""
    if not data:
        return {"count": 0, "mean": 0, "std": 0, "min": 0, "max": 0, "median": 0}
    arr = np.array(data)
    return {
        "count": int(len(arr)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "median": float(np.median(arr)),
        "q25": float(np.percentile(arr, 25)),
        "q75": float(np.percentile(arr, 75)),
        "skewness": float(scipy_stats.skew(arr)),
        "kurtosis": float(scipy_stats.kurtosis(arr)),
    }


def correlation_analysis(
    data_a: List[float],
    data_b: List[float],
    method: str = "pearson",
) -> EngineResult:
    """相关性分析。

    Args:
        data_a: 第一组数据。
        data_b: 第二组数据。
        method: "pearson" | "spearman" | "kendall"

    Returns:
        相关系数和p值。
    """
    if len(data_a) < 3 or len(data_b) < 3:
        return {"coefficient": 0.0, "p_value": 1.0, "method": method, "n": min(len(data_a), len(data_b))}

    if len(data_a) != len(data_b):
        n = min(len(data_a), len(data_b))
        data_a = data_a[:n]
        data_b = data_b[:n]

    method_map = {
        "pearson": scipy_stats.pearsonr,
        "spearman": scipy_stats.spearmanr,
        "kendall": scipy_stats.kendalltau,
    }
    func = method_map.get(method, scipy_stats.pearsonr)
    coefficient, p_value = func(data_a, data_b)

    return {
        "coefficient": float(coefficient),
        "p_value": float(p_value),
        "method": method,
        "n": len(data_a),
        "strength": _interpret_correlation(coefficient),
    }


def _interpret_correlation(r: float) -> str:
    """Interpret correlation strength."""
    r_abs = abs(r)
    if r_abs >= 0.8:
        return "very_strong"
    elif r_abs >= 0.6:
        return "strong"
    elif r_abs >= 0.4:
        return "moderate"
    elif r_abs >= 0.2:
        return "weak"
    else:
        return "very_weak"


def entropy_calculation(
    data: List[int],
    num_range: Tuple[int, int],
) -> EngineResult:
    """计算号码分布的信息熵。

    Shannon entropy measures the randomness/uniformity of number distribution.
    Higher entropy = more uniform distribution.

    Args:
        data: List of all drawn numbers.
        num_range: (min, max) for the number range.

    Returns:
        Entropy measures.
    """
    if not data:
        return {"shannon_entropy": 0.0, "max_entropy": 0.0, "normalized_entropy": 0.0, "count": 0}

    min_v, max_v = num_range
    range_size = max_v - min_v + 1

    # Count frequencies
    counter = Counter(data)
    total = len(data)

    # Shannon entropy
    entropy = 0.0
    for n in range(min_v, max_v + 1):
        p = counter.get(n, 0) / total
        if p > 0:
            entropy -= p * math.log2(p)

    # Maximum possible entropy (uniform distribution)
    max_entropy = math.log2(range_size) if range_size > 0 else 0

    # Normalized entropy (0-1, 1 = perfectly uniform)
    normalized = entropy / max_entropy if max_entropy > 0 else 0

    return {
        "shannon_entropy": round(entropy, 4),
        "max_entropy": round(max_entropy, 4),
        "normalized_entropy": round(normalized, 4),
        "range_size": range_size,
        "total_observations": total,
        "uniformity_percentage": round(normalized * 100, 2),
    }


def auto_correlation(
    data: List[float],
    lag: int = 1,
) -> EngineResult:
    """自相关分析 - 检测时间序列中的模式。

    Args:
        data: 时间序列数据。
        lag: 延迟期数。

    Returns:
        自相关系数。
    """
    if len(data) < lag + 3:
        return {"coefficient": 0.0, "lag": lag, "n": len(data)}

    a = np.array(data[:-lag])
    b = np.array(data[lag:])
    coeff, p_val = scipy_stats.pearsonr(a, b)

    return {
        "coefficient": float(coeff),
        "p_value": float(p_val),
        "lag": lag,
        "n": len(a),
    }
