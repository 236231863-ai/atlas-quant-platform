"""randomness - 随机性检验模块（v4.10）。

用数学检验验证历史开奖是否服从均匀随机分布，
证明任何基于历史频次的选号策略（热号/冷号/均衡）都没有统计优势。

这是"量化模型"的正确用法：证伪选号，而非推荐号码。
"""
from engine.lottery_quant.randomness.statistical_tests import (
    DISCLAIMER,
    RandomnessResult,
    chi_square_uniformity,
    runs_test,
    autocorrelation_test,
    full_randomness_audit,
)

__all__ = [
    "DISCLAIMER",
    "RandomnessResult",
    "chi_square_uniformity",
    "runs_test",
    "autocorrelation_test",
    "full_randomness_audit",
]
