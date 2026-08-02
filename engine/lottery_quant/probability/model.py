"""probability - 概率计算引擎（v3.9.0 Phase 1）。

基于组合数学计算各彩种奖级理论概率。

数学基础：
  大乐透  C(35,5) × C(12,2) = 21,425,712
  双色球  C(33,6) × C(16,1) = 17,721,088

重要说明：
  理论概率固定，任何号码组合中奖概率相同。
  系统只提供概率计算，不提供预测。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

DISCLAIMER = (
    "彩票开奖结果具有随机性，任何号码组合理论中奖概率相同。"
    "本数据仅为概率计算，不能预测未来开奖。"
)


@dataclass
class PrizeProbability:
    """一个奖级的理论概率。"""

    level: str              # 一等奖
    hit_desc: str           # 5+2
    ways: int               # 中奖组合数
    probability: float      # 概率（0-1）
    one_in: float           # 平均多少注中 1 注

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "hit": self.hit_desc,
            "ways": self.ways,
            "probability": round(self.probability, 10),
            "one_in": round(self.one_in, 2),
        }


@dataclass
class ProbabilityReport:
    """概率报告。"""

    lottery: str                    # dlt / ssq
    lottery_name: str               # 大乐透 / 双色球
    total_combinations: int         # 总组合数
    prizes: List[PrizeProbability] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def total_win_probability(self) -> float:
        return sum(p.probability for p in self.prizes)

    @property
    def first_prize_one_in(self) -> float:
        if self.prizes:
            return self.prizes[0].one_in
        return 0.0

    def summary_text(self) -> str:
        lines = [f"🎲 {self.lottery_name} 理论概率模型"]
        lines.append(f"· 总组合数：{self.total_combinations:,}")
        for p in self.prizes:
            lines.append(f"· {p.level}（{p.hit_desc}）：约 1/{p.one_in:,.0f}")
        lines.append(f"· 总中奖率：{self.total_win_probability * 100:.2f}%")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "lottery_name": self.lottery_name,
            "total_combinations": self.total_combinations,
            "prizes": [p.to_dict() for p in self.prizes],
            "total_win_probability": round(self.total_win_probability, 10),
            "first_prize_one_in": self.first_prize_one_in,
            "disclaimer": self.disclaimer,
        }


# 大乐透奖级规则：(前区命中, 后区命中) -> 等级
DLT_PRIZE_LEVELS = [
    ((5, 2), "一等奖"),
    ((5, 1), "二等奖"),
    ((5, 0), "三等奖"),
    ((4, 2), "四等奖"),
    ((4, 1), "五等奖"),
    ((3, 2), "六等奖"),
    ((4, 0), "七等奖"),
    ((3, 1), "八等奖"),
    ((2, 2), "八等奖"),
    ((3, 0), "九等奖"),
    ((1, 2), "九等奖"),
    ((2, 1), "九等奖"),
    ((0, 2), "九等奖"),
]

# 双色球奖级规则：(红球命中, 蓝球命中) -> 等级
SSQ_PRIZE_LEVELS = [
    ((6, 1), "一等奖"),
    ((6, 0), "二等奖"),
    ((5, 1), "三等奖"),
    ((5, 0), "四等奖"),
    ((4, 1), "四等奖"),
    ((4, 0), "五等奖"),
    ((3, 1), "五等奖"),
    ((2, 1), "六等奖"),
    ((1, 1), "六等奖"),
    ((0, 1), "六等奖"),
]


class ProbabilityModel:
    """概率模型（组合数学）。"""

    # ---------- 大乐透 ----------
    @staticmethod
    def dlt_total() -> int:
        """大乐透总组合数 C(35,5) × C(12,2)。"""
        return math.comb(35, 5) * math.comb(12, 2)

    @staticmethod
    def dlt_ways(front_hit: int, back_hit: int) -> int:
        """大乐透恰好命中 (front_hit, back_hit) 的组合数。"""
        f_ways = math.comb(5, front_hit) * math.comb(35 - 5, 5 - front_hit)
        b_ways = math.comb(2, back_hit) * math.comb(12 - 2, 2 - back_hit)
        return f_ways * b_ways

    # ---------- 双色球 ----------
    @staticmethod
    def ssq_total() -> int:
        """双色球总组合数 C(33,6) × 16。"""
        return math.comb(33, 6) * 16

    @staticmethod
    def ssq_ways(red_hit: int, blue_hit: int) -> int:
        """双色球恰好命中 (red_hit, blue_hit) 的组合数。"""
        r_ways = math.comb(6, red_hit) * math.comb(33 - 6, 6 - red_hit)
        b_ways = (1 if blue_hit else 15)
        return r_ways * b_ways

    # ---------- 报告 ----------
    @classmethod
    def dlt_report(cls) -> ProbabilityReport:
        total = cls.dlt_total()
        prizes = []
        for (fh, bh), level in DLT_PRIZE_LEVELS:
            ways = cls.dlt_ways(fh, bh)
            prob = ways / total
            prizes.append(PrizeProbability(
                level=level, hit_desc=f"{fh}+{bh}", ways=ways,
                probability=prob, one_in=total / ways if ways else 0,
            ))
        return ProbabilityReport(lottery="dlt", lottery_name="大乐透",
                                 total_combinations=total, prizes=prizes)

    @classmethod
    def ssq_report(cls) -> ProbabilityReport:
        total = cls.ssq_total()
        prizes = []
        for (rh, bh), level in SSQ_PRIZE_LEVELS:
            ways = cls.ssq_ways(rh, bh)
            prob = ways / total
            prizes.append(PrizeProbability(
                level=level, hit_desc=f"{rh}+{bh}", ways=ways,
                probability=prob, one_in=total / ways if ways else 0,
            ))
        return ProbabilityReport(lottery="ssq", lottery_name="双色球",
                                 total_combinations=total, prizes=prizes)


# ---------------- 便捷函数 ----------------
def dlt_probabilities() -> ProbabilityReport:
    """大乐透概率报告。"""
    return ProbabilityModel.dlt_report()


def ssq_probabilities() -> ProbabilityReport:
    """双色球概率报告。"""
    return ProbabilityModel.ssq_report()
