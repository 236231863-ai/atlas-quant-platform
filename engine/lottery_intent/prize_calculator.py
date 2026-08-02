"""lottery_intent - 奖金计算（PrizeCalculator）。

按大乐透/双色球中奖规则计算奖金。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# 大乐透规则：(front_hit, back_hit) -> (等级, 奖金)
DLT_PRIZE_TABLE = [
    ((5, 2), "一等奖", 5_000_000),
    ((5, 1), "二等奖", 180_000),
    ((5, 0), "三等奖", 10_000),
    ((4, 2), "四等奖", 3_000),
    ((4, 1), "五等奖", 300),
    ((3, 2), "六等奖", 200),
    ((4, 0), "七等奖", 100),
    ((3, 1), "八等奖", 15),
    ((2, 2), "八等奖", 15),
    ((3, 0), "九等奖", 5),
    ((1, 2), "九等奖", 5),
    ((2, 1), "九等奖", 5),
    ((0, 2), "九等奖", 5),
]

# 双色球规则：(red_hit, blue_hit) -> (等级, 奖金)
SSQ_PRIZE_TABLE = [
    ((6, 1), "一等奖", 5_000_000),
    ((6, 0), "二等奖", 100_000),
    ((5, 1), "三等奖", 3_000),
    ((5, 0), "四等奖", 200),
    ((4, 1), "四等奖", 200),
    ((4, 0), "五等奖", 10),
    ((3, 1), "五等奖", 10),
    ((2, 1), "六等奖", 5),
    ((1, 1), "六等奖", 5),
    ((0, 1), "六等奖", 5),
]


@dataclass
class PrizeResult:
    """单注奖金结果。"""

    prize_level: Optional[str] = None
    amount: float = 0.0
    front_hit: int = 0
    back_hit: int = 0

    @property
    def won(self) -> bool:
        return self.amount > 0


class PrizeCalculator:
    """奖金计算器。"""

    @staticmethod
    def calculate(front_hit: int, back_hit: int, lottery: str = "dlt") -> PrizeResult:
        """按命中数计算奖金。"""
        table = DLT_PRIZE_TABLE if lottery == "dlt" else SSQ_PRIZE_TABLE
        for (fh, bh), level, amount in table:
            if front_hit >= fh and back_hit >= bh:
                return PrizeResult(prize_level=level, amount=amount, front_hit=front_hit, back_hit=back_hit)
        return PrizeResult(front_hit=front_hit, back_hit=back_hit)

    @classmethod
    def total_for(cls, matches: list, lottery: str = "dlt") -> dict:
        """汇总多注奖金。matches: [DrawMatch]"""
        total = 0.0
        details = []
        won_notes = 0
        for m in matches:
            r = cls.calculate(m.front_hits, m.back_hits, lottery)
            total += r.amount
            if r.won:
                won_notes += 1
            details.append({
                "front_hit": r.front_hit, "back_hit": r.back_hit,
                "level": r.prize_level, "amount": r.amount,
            })
        return {"total": total, "won_notes": won_notes, "details": details}
