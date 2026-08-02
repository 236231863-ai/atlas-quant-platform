"""probability - 概率计算引擎（v3.9.0 Phase 1）。

基于组合数学计算各彩种奖级理论概率。

说明：理论概率固定，任何号码组合概率相同。
"""
from .model import (
    ProbabilityModel,
    PrizeProbability,
    ProbabilityReport,
    dlt_probabilities,
    ssq_probabilities,
)

__all__ = [
    "ProbabilityModel",
    "PrizeProbability",
    "ProbabilityReport",
    "dlt_probabilities",
    "ssq_probabilities",
]
