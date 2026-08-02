"""evaluation_v2 - 随机基准（Random Baseline）。

与策略同口径的「随机选号」对照实验：
  每期随机选择 front_n 个前区 + back_n 个后区，按相同中奖规则计奖。
  多次模拟（默认 50 次）取平均，得到随机基准的 ROI 与区间。

用途：判断策略收益是否显著优于「运气」。若策略 ROI 接近或低于随机基准，
则策略没有统计意义上的优势。
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .split import temporal_split


@dataclass
class PrizeRule:
    """一种奖项的中奖条件与奖金。"""

    front_hit: int
    back_hit: int
    name: str
    amount: float


# 大乐透官方奖金（简化，与 desktop/backtest_page.PRIZES 对齐）
DLT_PRIZES = [
    PrizeRule(5, 2, "一等奖", 5_000_000),
    PrizeRule(5, 1, "二等奖", 180_000),
    PrizeRule(5, 0, "三等奖", 10_000),
    PrizeRule(4, 2, "四等奖", 3_000),
    PrizeRule(4, 1, "五等奖", 300),
    PrizeRule(3, 2, "六等奖", 200),
    PrizeRule(4, 0, "七等奖", 100),
    PrizeRule(3, 1, "八等奖", 15),
    PrizeRule(2, 2, "八等奖", 15),
    PrizeRule(3, 0, "九等奖", 5),
    PrizeRule(1, 2, "九等奖", 5),
    PrizeRule(2, 1, "九等奖", 5),
    PrizeRule(0, 2, "九等奖", 5),
]


def _grade(front_hit: int, back_hit: int, prizes: List[PrizeRule] = DLT_PRIZES) -> Tuple[Optional[str], float]:
    for r in prizes:
        if front_hit >= r.front_hit and back_hit >= r.back_hit:
            return r.name, r.amount
    return None, 0.0


class RandomBaseline:
    """随机选号基准。

    Args:
        front_range: (min, max) 前区号码范围。
        back_range: (min, max) 后区号码范围。
        front_n: 前区选号个数。
        back_n: 后区选号个数。
        ticket_cost: 单注价格。
        n_simulations: 模拟次数（越多越稳定）。
        seed: 随机种子（可复现）。
    """

    def __init__(
        self,
        front_range: Tuple[int, int] = (1, 35),
        back_range: Tuple[int, int] = (1, 12),
        front_n: int = 5,
        back_n: int = 2,
        ticket_cost: float = 2.0,
        n_simulations: int = 50,
        seed: Optional[int] = None,
    ):
        self.front_range = front_range
        self.back_range = back_range
        self.front_n = front_n
        self.back_n = back_n
        self.ticket_cost = ticket_cost
        self.n_simulations = n_simulations
        self._seed = seed

    def _random_ticket(self, rng: random.Random) -> Tuple[List[int], List[int]]:
        front = sorted(rng.sample(range(self.front_range[0], self.front_range[1] + 1), self.front_n))
        back = sorted(rng.sample(range(self.back_range[0], self.back_range[1] + 1), self.back_n))
        return front, back

    def _run_once(self, draws: List) -> dict:
        """单次随机回测：对每期随机选号并与实际开奖比对。"""
        rng = random.Random(self._seed)
        equity = 0.0
        revenue = 0.0
        cost = 0.0
        wins = 0
        for d in draws:
            front, back = self._random_ticket(rng)
            fh = len(set(front) & set(d.front))
            bh = len(set(back) & set(d.back))
            _, amount = _grade(fh, bh)
            revenue += amount
            cost += self.ticket_cost
            equity += amount - self.ticket_cost
            if amount > 0:
                wins += 1
        roi = (revenue - cost) / cost * 100 if cost else 0.0
        return {
            "roi": roi,
            "equity": equity,
            "revenue": revenue,
            "cost": cost,
            "wins": wins,
            "n_bets": len(draws),
            "win_rate": wins / len(draws) if draws else 0.0,
        }

    def evaluate(self, draws: List) -> dict:
        """多次模拟，返回随机基准汇总（均值/区间/中位数 ROI）。"""
        results = []
        seeds = None
        for i in range(self.n_simulations):
            if self._seed is not None:
                self._seed = self._seed + i * 1000  # 每次不同种子
            results.append(self._run_once(draws))
        rois = sorted(r["roi"] for r in results)
        n = len(rois)
        mean = sum(rois) / n
        median = rois[n // 2]
        lo, hi = rois[int(n * 0.05)], rois[min(n - 1, int(n * 0.95))]
        wins = sum(r["wins"] for r in results)
        win_rate = wins / (self.n_simulations * (len(draws) or 1))
        return {
            "n_simulations": self.n_simulations,
            "roi_mean": mean,
            "roi_median": median,
            "roi_p5": lo,
            "roi_p95": hi,
            "roi_range": (lo, hi),
            "win_rate": win_rate,
            "n_bets": len(draws) if draws else 0,
        }
