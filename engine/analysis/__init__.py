"""
Atlas Quant Platform - Analysis Engine.

统计分析引擎:
- frequency: 号码出现频率分析
- gap: 号码遗漏分析
- distribution: 分布分析 (奇偶、高低、区间、和值、跨度)

所有函数为纯计算，无副作用。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.types.models import DrawRecordData
from engine.analysis.calculators.frequency import frequency_analysis
from engine.analysis.calculators.gap import gap_analysis
from engine.analysis.calculators.distribution import distribution_analysis


def calculate_frequency(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """分析号码出现频率。

    Args:
        draws: 开奖记录列表，按时间先后排序。
        main_range: (最小值, 最大值) 主号码范围。
        bonus_range: (最小值, 最大值) 特别号码范围。

    Returns:
        频率统计结果字典。
    """
    return frequency_analysis(draws, main_range, bonus_range)


def calculate_gap(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
    bonus_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """分析号码遗漏情况。

    Args:
        draws: 开奖记录列表，按时间先后排序。
        main_range: (最小值, 最大值) 主号码范围。
        bonus_range: (最小值, 最大值) 特别号码范围。

    Returns:
        遗漏统计结果字典。
    """
    return gap_analysis(draws, main_range, bonus_range)


def calculate_distribution(
    draws: List[DrawRecordData],
    main_range: Tuple[int, int],
) -> Dict[str, Any]:
    """分析号码分布情况。

    计算: 奇偶比、高低比、区间分布、和值分布、跨度分布。

    Args:
        draws: 开奖记录列表。
        main_range: (最小值, 最大值) 主号码范围。

    Returns:
        分布统计结果字典。
    """
    return distribution_analysis(draws, main_range)
