"""simulation - 蒙特卡洛模拟引擎（v3.9.0 Phase 3）。

随机生成 10 万次开奖，模拟用户投注组合的中奖覆盖情况。

输出 SimulationReport：
  - 模拟次数
  - 一等奖命中次数 / 二等奖命中次数 / 小奖次数
  - 覆盖率（至少一注中奖的模拟占比）
  - 期望奖金

重要声明：模拟结果不代表未来，开奖结果具有随机性。
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from engine.lottery_intent.prize_calculator import PrizeCalculator

DISCLAIMER = "模拟结果不代表未来。彩票开奖结果具有随机性。"

# 彩种参数：前区范围/数量，后区范围/数量
LOTTERY_PARAMS = {
    "dlt": {"front_max": 35, "front_n": 5, "back_max": 12, "back_n": 2},
    "ssq": {"front_max": 33, "front_n": 6, "back_max": 16, "back_n": 1},
}


@dataclass
class SimulationReport:
    """模拟报告。"""

    lottery: str = "dlt"
    lottery_name: str = "大乐透"
    trials: int = 0
    note_count: int = 0
    first_prize_hits: int = 0
    second_prize_hits: int = 0
    minor_prize_hits: int = 0          # 三等奖及以下中奖次数
    total_win_simulations: int = 0     # 至少一注中奖的模拟次数
    total_prize: float = 0.0           # 模拟总奖金
    disclaimer: str = DISCLAIMER

    @property
    def coverage_rate(self) -> float:
        """覆盖率：至少一注中奖的模拟占比。"""
        return self.total_win_simulations / self.trials if self.trials else 0.0

    @property
    def expected_return(self) -> float:
        """单次模拟期望奖金（元）。"""
        return self.total_prize / self.trials if self.trials else 0.0

    def to_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "lottery_name": self.lottery_name,
            "trials": self.trials,
            "note_count": self.note_count,
            "first_prize_hits": self.first_prize_hits,
            "second_prize_hits": self.second_prize_hits,
            "minor_prize_hits": self.minor_prize_hits,
            "total_win_simulations": self.total_win_simulations,
            "coverage_rate": round(self.coverage_rate, 6),
            "expected_return": round(self.expected_return, 4),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = [f"🎲 蒙特卡洛模拟（{self.lottery_name}）"]
        lines.append(f"· 模拟次数：{self.trials:,} 次")
        lines.append(f"· 投注注数：{self.note_count} 注")
        lines.append(f"· 一等奖命中：{self.first_prize_hits} 次")
        lines.append(f"· 二等奖命中：{self.second_prize_hits} 次")
        lines.append(f"· 小奖命中（3-9等）：{self.minor_prize_hits} 次")
        lines.append(f"· 覆盖率（至少一注中奖）：{self.coverage_rate * 100:.2f}%")
        lines.append(f"· 单次期望奖金：¥{self.expected_return:.2f}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class SimulationEngine:
    """蒙特卡洛模拟引擎。"""

    @staticmethod
    def _draw(rng: random.Random, lottery: str) -> tuple:
        """随机生成一注开奖。"""
        p = LOTTERY_PARAMS[lottery]
        front = tuple(sorted(rng.sample(range(1, p["front_max"] + 1), p["front_n"])))
        back = tuple(sorted(rng.sample(range(1, p["back_max"] + 1), p["back_n"])))
        return front, back

    @staticmethod
    def _ticket_sets(tickets: List[dict], lottery: str) -> list:
        """预计算用户票据集合。"""
        p = LOTTERY_PARAMS[lottery]
        out = []
        for t in tickets:
            front = set(t.get("front", []))
            back = set(t.get("back", []))
            if len(front) != p["front_n"] or len(back) != p["back_n"]:
                continue
            out.append((front, back))
        return out

    @classmethod
    def simulate(cls, tickets: List[dict], lottery: str = "dlt",
                 trials: int = 100_000, seed: Optional[int] = None) -> SimulationReport:
        """执行蒙特卡洛模拟。

        tickets: [{"front": [...], "back": [...]}]
        trials: 模拟次数（默认 10 万）
        """
        report = SimulationReport(
            lottery=lottery,
            lottery_name="大乐透" if lottery == "dlt" else "双色球",
            trials=trials,
            note_count=len(tickets),
        )
        sets = cls._ticket_sets(tickets, lottery)
        if not sets or trials <= 0:
            return report

        rng = random.Random(seed)
        p = LOTTERY_PARAMS[lottery]

        for _ in range(trials):
            draw_front, draw_back = cls._draw(rng, lottery)
            won_this_sim = False
            for front, back in sets:
                fh = len(front & set(draw_front))
                bh = len(back & set(draw_back))
                r = PrizeCalculator.calculate(fh, bh, lottery)
                if not r.won:
                    continue
                won_this_sim = True
                report.total_prize += r.amount
                if r.prize_level == "一等奖":
                    report.first_prize_hits += 1
                elif r.prize_level == "二等奖":
                    report.second_prize_hits += 1
                else:
                    report.minor_prize_hits += 1
            if won_this_sim:
                report.total_win_simulations += 1

        return report


def simulate_coverage(tickets: List[dict], lottery: str = "dlt",
                      trials: int = 100_000, seed: Optional[int] = None) -> SimulationReport:
    """便捷函数：模拟中奖覆盖。"""
    return SimulationEngine.simulate(tickets, lottery, trials=trials, seed=seed)
