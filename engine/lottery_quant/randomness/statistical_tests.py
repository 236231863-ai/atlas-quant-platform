"""randomness.statistical_tests - 随机性统计检验（v4.10）。

三个检验 + 汇总审计：
  1. 卡方拟合优度（chi-square goodness-of-fit）：号码频次是否与均匀分布一致
  2. 游程检验（Wald-Wolfowitz runs test）：0/1 序列（如某号码是否出现）是否随机
  3. 自相关检验（lag-1 autocorrelation）：数值序列（如和值）是否无自相关

核心结论：所有检验若均无法拒绝"均匀随机"假设，则说明——
任何基于历史频次的选号策略（热号/冷号/均衡）在统计上都没有优势。

严格红线：本模块只证伪选号，不做任何预测/推荐。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from scipy import stats as scipy_stats

DISCLAIMER = (
    "随机性检验仅用于验证历史数据是否服从均匀随机分布，"
    "不构成任何选号建议。开奖结果独立同分布，历史不预示未来。"
)

# 各彩种号码范围
LOTTERY_RANGES = {
    "dlt": {"front": (1, 35), "back": (1, 12)},
    "ssq": {"front": (1, 33), "back": (1, 16)},
}


@dataclass
class RandomnessResult:
    """一次随机性检验结果。"""

    test_name: str
    statistic: float
    p_value: float
    significant: bool  # True = 拒绝"随机"假设（p < alpha）
    conclusion: str
    alpha: float = 0.05
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "test": self.test_name,
            "statistic": round(self.statistic, 4),
            "p_value": round(self.p_value, 6),
            "significant": self.significant,
            "conclusion": self.conclusion,
            "alpha": self.alpha,
            "disclaimer": self.disclaimer,
        }


def _result(test_name: str, statistic: float, p_value: float, alpha: float = 0.05) -> RandomnessResult:
    """统一构造检验结果与结论。"""
    significant = bool(p_value < alpha)
    if significant:
        conclusion = "拒绝均匀随机假设（存在统计显著差异，需核查数据来源）"
    else:
        conclusion = "与均匀随机分布一致（无法拒绝随机假设，无选号优势）"
    return RandomnessResult(
        test_name=test_name,
        statistic=float(statistic),
        p_value=float(p_value),
        significant=significant,
        conclusion=conclusion,
        alpha=alpha,
    )


def chi_square_uniformity(
    observed: Sequence[float],
    expected: Optional[Sequence[float]] = None,
    test_name: str = "卡方拟合优度",
    alpha: float = 0.05,
) -> RandomnessResult:
    """卡方拟合优度检验：观测频次是否与均匀分布（或给定期望）一致。

    Args:
        observed: 观测频次列表（如各号码出现次数）。
        expected: 期望频次列表；None 表示均匀分布（等频）。
    """
    obs = [float(x) for x in observed]
    if len(obs) < 2 or sum(obs) <= 0:
        return RandomnessResult(test_name, 0.0, 1.0, False, "样本不足，无法检验", alpha)
    if expected is None:
        mean = sum(obs) / len(obs)
        exp = [mean] * len(obs)
    else:
        exp = [float(x) for x in expected]
        if len(exp) != len(obs):
            return RandomnessResult(test_name, 0.0, 1.0, False, "期望与观测长度不一致", alpha)
    # scipy 要求期望全正
    if any(e <= 0 for e in exp):
        return RandomnessResult(test_name, 0.0, 1.0, False, "期望频次非正，无法检验", alpha)
    stat, p = scipy_stats.chisquare(obs, f_exp=exp)
    return _result(test_name, stat, p, alpha)


def runs_test(
    sequence: Sequence[int],
    test_name: str = "游程检验",
    alpha: float = 0.05,
) -> RandomnessResult:
    """Wald-Wolfowitz 游程检验：0/1 序列是否随机排列。

    Args:
        sequence: 由 0/1（或二值）组成的序列，如某号码逐期是否出现。
    """
    seq = [1 if x else 0 for x in sequence]
    n = len(seq)
    if n < 2:
        return RandomnessResult(test_name, 0.0, 1.0, False, "样本不足，无法检验", alpha)
    n1 = sum(seq)
    n2 = n - n1
    if n1 == 0 or n2 == 0:
        # 全 0 或全 1：无游程变化，视为无法区分随机性（p=1，不显著）
        return RandomnessResult(test_name, 0.0, 1.0, False, "序列全同，无游程变化", alpha)

    # 游程数 R = 相邻值变化的次数 + 1
    runs = 1
    for i in range(1, n):
        if seq[i] != seq[i - 1]:
            runs += 1

    mean = 1.0 + 2.0 * n1 * n2 / n
    var = (2.0 * n1 * n2 * (2.0 * n1 * n2 - n)) / (n * n * (n - 1))
    if var <= 0:
        return RandomnessResult(test_name, runs - mean, 1.0, False, "方差为零，无法检验", alpha)
    z = (runs - mean) / math.sqrt(var)
    p = 2.0 * (1.0 - scipy_stats.norm.cdf(abs(z)))
    return _result(test_name, z, p, alpha)


def autocorrelation_test(
    sequence: Sequence[float],
    lag: int = 1,
    test_name: str = "自相关检验",
    alpha: float = 0.05,
) -> RandomnessResult:
    """lag-1 自相关检验：数值序列是否无自相关（随机）。

    Args:
        sequence: 数值序列，如每期和值、每期某号码出现次数。
        lag: 滞后阶数（默认 1）。
    """
    seq = [float(x) for x in sequence]
    n = len(seq)
    if n < lag + 3:
        return RandomnessResult(test_name, 0.0, 1.0, False, "样本不足，无法检验", alpha)

    mean = sum(seq) / n
    denom = sum((x - mean) ** 2 for x in seq)
    if denom <= 0:
        # 序列恒定（方差为 0），无自相关可谈
        return RandomnessResult(test_name, 0.0, 1.0, False, "序列恒定，无自相关", alpha)

    numer = sum((seq[i] - mean) * (seq[i + lag] - mean) for i in range(n - lag))
    r = numer / denom

    # 随机假设下，r 近似 N(0, 1/n)
    z = r * math.sqrt(n)
    p = 2.0 * (1.0 - scipy_stats.norm.cdf(abs(z)))
    return _result(test_name, z, p, alpha)


def _freq_counts(draws, field: str, rng: tuple) -> List[int]:
    """统计指定号码范围内各号码的出现次数。"""
    lo, hi = rng
    counts = [0] * (hi - lo + 1)
    for d in draws:
        nums = getattr(d, field, None) or []
        for num in nums:
            if lo <= num <= hi:
                counts[num - lo] += 1
    return counts


def full_randomness_audit(draws, lottery: str = "dlt", alpha: float = 0.05) -> dict:
    """对历史开奖做完整随机性审计，输出所有检验 + 总结论。

    Args:
        draws: 开奖记录列表，每条记录有 front / back 属性（List[int]）。
        lottery: "dlt" 或 "ssq"。

    Returns:
        dict：包含各检验结果与总结论（无预测/推荐）。
    """
    ranges = LOTTERY_RANGES.get(lottery, LOTTERY_RANGES["dlt"])
    results: List[RandomnessResult] = []

    # 1. 前区频次卡方
    front_freq = _freq_counts(draws, "front", ranges["front"])
    results.append(
        chi_square_uniformity(front_freq, test_name=f"{lottery} 前区频次卡方", alpha=alpha)
    )

    # 2. 后区频次卡方
    back_freq = _freq_counts(draws, "back", ranges["back"])
    results.append(
        chi_square_uniformity(back_freq, test_name=f"{lottery} 后区频次卡方", alpha=alpha)
    )

    # 3. 出现最多号码的出现序列游程检验（0/1：该号码每期是否出现）
    if draws:
        lo, hi = ranges["front"]
        # 找出现次数最多的号码
        front_freq_full = _freq_counts(draws, "front", ranges["front"])
        hot_num = lo + max(range(len(front_freq_full)), key=lambda i: front_freq_full[i])
        appear_seq = [1 if hot_num in (getattr(d, "front", None) or []) else 0 for d in draws]
        results.append(
            runs_test(appear_seq, test_name=f"{lottery} 最高频号码({hot_num})出现游程", alpha=alpha)
        )

    # 4. 前区和值序列自相关
    if draws:
        sums = [sum(getattr(d, "front", None) or []) for d in draws]
        results.append(
            autocorrelation_test(sums, test_name=f"{lottery} 前区和值自相关", alpha=alpha)
        )

    # 总结论
    significant_tests = [r for r in results if r.significant]
    if significant_tests:
        summary = (
            f"{len(significant_tests)}/{len(results)} 项检验出现统计显著差异，"
            "建议核查数据来源是否完整可信，而非据此选号。"
        )
    else:
        summary = (
            f"全部 {len(results)} 项检验均与均匀随机分布一致："
            "历史频次与顺序没有任何超出随机波动的规律，"
            "任何基于历史频次的选号策略（热号/冷号/均衡）在统计上都没有优势。"
        )

    return {
        "lottery": lottery,
        "total_draws": len(draws),
        "alpha": alpha,
        "tests": [r.to_dict() for r in results],
        "summary": summary,
        "disclaimer": DISCLAIMER,
    }
