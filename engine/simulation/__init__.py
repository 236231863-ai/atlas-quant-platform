"""
Atlas Quant Platform - Simulation Engine.

蒙特卡洛模拟引擎，用于随机组合模拟和统计分布分析。
纯计算: 无IO、无数据库、无副作用。
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from core.types.models import DrawRecordData
from engine import EngineResult


def monte_carlo_simulation(
    num_simulations: int,
    num_draws: int,
    main_range: Tuple[int, int],
    main_count: int,
    bonus_range: Optional[Tuple[int, int]] = None,
    bonus_count: int = 0,
    selection_func: Optional[Callable] = None,
    random_seed: Optional[int] = None,
) -> EngineResult:
    """执行蒙特卡洛模拟。

    随机生成大量号码组合，分析统计分布特征。

    Args:
        num_simulations: 模拟次数。
        num_draws: 每次模拟的期数。
        main_range: (min, max) 主号码范围。
        main_count: 每期主号码数量。
        bonus_range: (min, max) 特别号码范围。
        bonus_count: 每期特别号码数量。
        selection_func: 自定义选号函数。None=纯随机。
        random_seed: 随机种子，控制可复现性。

    Returns:
        模拟结果字典。
    """
    rng = random.Random(random_seed)
    min_m, max_m = main_range

    if selection_func is None:
        selection_func = _random_selection

    all_main_numbers: List[int] = []
    all_bonus_numbers: List[int] = []

    for sim in range(num_simulations):
        for _ in range(num_draws):
            main = selection_func(rng, min_m, max_m, main_count)
            all_main_numbers.extend(main)

            if bonus_range and bonus_count > 0:
                min_b, max_b = bonus_range
                bonus = _random_selection(rng, min_b, max_b, bonus_count)
                all_bonus_numbers.extend(bonus)

    # Analyze main number distribution
    main_freq = Counter(all_main_numbers)
    total_main = len(all_main_numbers)

    main_stats = _simulation_stats(
        main_freq, main_range, main_count, num_simulations, num_draws, total_main, rng
    )

    # Analyze bonus number distribution
    bonus_stats = None
    if bonus_range and bonus_count > 0 and all_bonus_numbers:
        bonus_freq = Counter(all_bonus_numbers)
        total_bonus = len(all_bonus_numbers)
        bonus_stats = _simulation_stats(
            bonus_freq, bonus_range, bonus_count, num_simulations, num_draws, total_bonus, rng
        )

    return {
        "analysis_type": "monte_carlo",
        "num_simulations": num_simulations,
        "num_draws_per_simulation": num_draws,
        "total_combinations_generated": num_simulations * num_draws,
        "random_seed": random_seed,
        "main_numbers": main_stats,
        "bonus_numbers": bonus_stats,
    }


def _random_selection(
    rng: random.Random,
    min_v: int,
    max_v: int,
    count: int,
) -> List[int]:
    """纯随机选择不重复的号码。"""
    return sorted(rng.sample(range(min_v, max_v + 1), count))


def _simulation_stats(
    freq: Counter,
    num_range: Tuple[int, int],
    count_per_draw: int,
    num_simulations: int,
    num_draws: int,
    total_occurrences: int,
    rng: random.Random,
) -> Dict[str, Any]:
    """Compute simulation statistics for a number set."""
    min_v, max_v = num_range
    range_size = max_v - min_v + 1
    expected_per_number = total_occurrences / range_size if range_size > 0 else 0

    frequencies = {}
    observed: List[float] = []
    for n in range(min_v, max_v + 1):
        c = freq.get(n, 0)
        frequencies[str(n)] = c
        observed.append(float(c))

    # Chi-square test
    expected_list = [expected_per_number] * range_size if expected_per_number > 0 else [0.0] * range_size
    chi_sq = None
    if expected_per_number > 0 and total_occurrences > 0:
        from scipy import stats as scipy_stats
        try:
            stat, p_val = scipy_stats.chisquare(observed, expected_list)
            chi_sq = {"statistic": float(stat), "p_value": float(p_val), "significant": p_val < 0.05}
        except Exception:
            chi_sq = {"error": "Chi-square computation failed"}

    # Frequency rates
    sorted_freq = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)

    # Entropy calculation
    entropy_val = 0.0
    for n in range(min_v, max_v + 1):
        p = freq.get(n, 0) / total_occurrences if total_occurrences > 0 else 0
        if p > 0:
            entropy_val -= p * math.log2(p)
    max_entropy = math.log2(range_size)
    normalized_entropy = entropy_val / max_entropy if max_entropy > 0 else 0

    return {
        "range": {"min": min_v, "max": max_v, "size": range_size},
        "count_per_draw": count_per_draw,
        "total_occurrences": total_occurrences,
        "expected_per_number": round(expected_per_number, 4),
        "frequencies": frequencies,
        "sorted_by_frequency": [(int(k), v) for k, v in sorted_freq],
        "chi_square": chi_sq,
        "entropy": {
            "shannon_entropy": round(entropy_val, 4),
            "normalized_entropy": round(normalized_entropy, 4),
            "uniformity_pct": round(normalized_entropy * 100, 2),
        },
    }


def expected_value_analysis(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    main_count: int,
) -> EngineResult:
    """计算号码的理论期望值与实际出现次数的偏差。

    Args:
        draws: 历史开奖记录。
        main_range: (min, max) 主号码范围。
        main_count: 每期主号码数量。

    Returns:
        期望值分析结果。
    """
    if not draws:
        return {"total_draws": 0, "numbers": {}}

    min_v, max_v = main_range
    range_size = max_v - min_v + 1

    # Count actual occurrences
    counter: Counter[int] = Counter()
    for draw in draws:
        counter.update(draw.main_numbers)

    total_draws = len(draws)
    expected_per_draw = main_count
    expected_total = total_draws * main_count
    expected_per_number = expected_total / range_size if range_size > 0 else 0

    numbers: Dict[str, Dict[str, Any]] = {}
    z_scores: List[float] = []
    for n in range(min_v, max_v + 1):
        actual = counter.get(n, 0)
        deviation = actual - expected_per_number
        deviation_pct = (deviation / expected_per_number * 100) if expected_per_number > 0 else 0

        # Z-score approximation (binomial)
        expected_prob = expected_per_number / expected_total if expected_total > 0 else 0
        std_dev = math.sqrt(expected_total * expected_prob * (1 - expected_prob)) if expected_prob > 0 else 0
        z = deviation / std_dev if std_dev > 0 else 0

        numbers[str(n)] = {
            "actual": actual,
            "expected": round(expected_per_number, 2),
            "deviation": round(deviation, 2),
            "deviation_pct": round(deviation_pct, 2),
            "z_score": round(z, 4),
        }
        z_scores.append(z)

    # Overall stats
    max_pos_z = max(z_scores) if z_scores else 0
    most_over = [{"number": n, "z_score": z} for n, z in
                 sorted([(int(k), v["z_score"]) for k, v in numbers.items()], key=lambda x: x[1], reverse=True)[:5]]
    most_under = [{"number": n, "z_score": z} for n, z in
                  sorted([(int(k), v["z_score"]) for k, v in numbers.items()], key=lambda x: x[1])[:5]]

    return {
        "analysis_type": "expected_value",
        "total_draws": total_draws,
        "total_numbers_drawn": expected_total,
        "expected_per_number": round(expected_per_number, 2),
        "numbers": numbers,
        "most_overrepresented": most_over,
        "most_underrepresented": most_under,
        "max_positive_z": round(max_pos_z, 4),
    }
