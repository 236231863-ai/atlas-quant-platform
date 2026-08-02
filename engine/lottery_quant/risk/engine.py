"""risk - 资金风险引擎（v3.9.0 Phase 4）。

输入：每期投入金额、周期、投注次数
输出：RiskReport
  - 年度投入
  - 最大损失（全部未中奖情形）
  - 预计回报（理论返还率）
  - 亏损概率（模拟：年总奖金 < 年投入）
  - 风险等级 A/B/C/D

重要声明：彩票为负期望游戏，长期亏损是大概率事件。
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from engine.lottery_quant.simulation.monte_carlo import SimulationEngine

DISCLAIMER = "彩票为负期望游戏，长期亏损是大概率事件。请理性购彩。"

# 彩种理论返还率（官方设定返还率约 50-55%）
RETURN_RATE = {"dlt": 0.55, "ssq": 0.55}


def _risk_level(annual_investment: float) -> str:
    """风险等级：按年度投入金额。"""
    if annual_investment <= 1000:
        return "A"
    if annual_investment <= 3000:
        return "B"
    if annual_investment <= 10_000:
        return "C"
    return "D"


@dataclass
class RiskReport:
    """风险报告。"""

    lottery: str = "dlt"
    lottery_name: str = "大乐透"
    cost_per_note: float = 2.0
    notes_per_draw: int = 1
    draws_per_week: int = 3
    weeks: int = 52
    annual_draws: int = 0
    annual_investment: float = 0.0
    max_loss: float = 0.0
    expected_return: float = 0.0
    lose_probability: float = 0.0     # 0-1
    risk_level: str = "A"
    disclaimer: str = DISCLAIMER

    @property
    def expected_profit(self) -> float:
        """预计盈亏（负 = 亏损）。"""
        return self.expected_return - self.annual_investment

    def to_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "lottery_name": self.lottery_name,
            "annual_draws": self.annual_draws,
            "annual_investment": round(self.annual_investment, 2),
            "max_loss": round(self.max_loss, 2),
            "expected_return": round(self.expected_return, 2),
            "expected_profit": round(self.expected_profit, 2),
            "lose_probability": round(self.lose_probability, 4),
            "risk_level": self.risk_level,
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = [f"💰 资金风险分析（{self.lottery_name}）"]
        lines.append(f"· 年度投注：{self.annual_draws} 期")
        lines.append(f"· 年度投入：¥{self.annual_investment:,.0f}")
        lines.append(f"· 最大损失：¥{self.max_loss:,.0f}（全部未中奖）")
        lines.append(f"· 预计回报：¥{self.expected_return:,.0f}（理论返还率 {RETURN_RATE.get(self.lottery, 0.55) * 100:.0f}%）")
        lines.append(f"· 预计盈亏：¥{self.expected_profit:,.0f}")
        lines.append(f"· 亏损概率：{self.lose_probability * 100:.1f}%")
        lines.append(f"· 娱乐风险等级：{self.risk_level}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class RiskEngine:
    """资金风险引擎。"""

    @staticmethod
    def _random_tickets(notes: int, lottery: str, rng: random.Random) -> List[dict]:
        """生成 notes 注随机号码（用于模拟）。"""
        if lottery == "dlt":
            return [{"front": sorted(rng.sample(range(1, 36), 5)),
                     "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(notes)]
        return [{"front": sorted(rng.sample(range(1, 34), 6)),
                 "back": [rng.randint(1, 16)]} for _ in range(notes)]

    @classmethod
    def analyze(cls, cost_per_note: float = 2.0, notes_per_draw: int = 1,
                draws_per_week: int = 3, weeks: int = 52, lottery: str = "dlt",
                tickets: Optional[List[dict]] = None,
                n_years: int = 300, seed: int = 42) -> RiskReport:
        """资金风险分析。

        参数：
          cost_per_note  每注成本（元）
          notes_per_draw 每期注数
          draws_per_week 每周投注次数
          weeks          周期周数
          lottery        dlt / ssq
          tickets        用户实际票据（可选，用其注数）
        """
        notes = notes_per_draw
        if tickets:
            notes = len(tickets)
        annual_draws = max(1, draws_per_week * weeks)
        annual_investment = cost_per_note * notes * annual_draws

        # 预计回报（理论返还率）
        expected_return = annual_investment * RETURN_RATE.get(lottery, 0.55)

        # 亏损概率：模拟 n_years 个年度，统计年总奖金 < 年投入的比例
        rng = random.Random(seed)
        loss_years = 0
        for i in range(n_years):
            tk = tickets or cls._random_tickets(notes, lottery, rng)
            rep = SimulationEngine.simulate(tk, lottery, trials=annual_draws,
                                            seed=seed * 1000 + i)
            if rep.total_prize < annual_investment:
                loss_years += 1
        lose_probability = loss_years / n_years if n_years else 0.0

        return RiskReport(
            lottery=lottery,
            lottery_name="大乐透" if lottery == "dlt" else "双色球",
            cost_per_note=cost_per_note,
            notes_per_draw=notes,
            draws_per_week=draws_per_week,
            weeks=weeks,
            annual_draws=annual_draws,
            annual_investment=annual_investment,
            max_loss=annual_investment,
            expected_return=expected_return,
            lose_probability=lose_probability,
            risk_level=_risk_level(annual_investment),
        )


def analyze_risk(cost_per_note: float = 2.0, notes_per_draw: int = 1,
                 draws_per_week: int = 3, weeks: int = 52, lottery: str = "dlt",
                 tickets: Optional[List[dict]] = None,
                 n_years: int = 300, seed: int = 42) -> RiskReport:
    """便捷函数：资金风险分析。"""
    return RiskEngine.analyze(cost_per_note, notes_per_draw, draws_per_week,
                              weeks, lottery, tickets, n_years, seed)
