"""backtest - 策略回测器（v3.9.0 Phase 6）。

复用 engine/evaluation_v2：
  - run_backtest_with_evaluation（hot/cold/balanced + 随机基准）
  - 补 random 策略（与热/冷/均衡同口径）

输出 StrategyReport：各策略表现 + 与随机基准比较。
禁止盈利保证。
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from engine.evaluation_v2.metrics import run_backtest_with_evaluation, PerformanceReport
from engine.evaluation_v2.baseline import _grade, DLT_PRIZES

DISCLAIMER = "彩票开奖为独立随机事件，历史回测不代表未来，不构成盈利保证。"

STRATEGY_METHODS = ["hot", "cold", "balanced", "random"]

STRATEGY_NAMES = {
    "hot": "热号策略",
    "cold": "冷号策略",
    "balanced": "均衡策略",
    "random": "随机策略",
}


@dataclass
class StrategyReport:
    """策略回测报告。"""

    periods: int = 0
    strategies: dict = field(default_factory=dict)      # name -> PerformanceReport
    disclaimer: str = DISCLAIMER

    def best_strategy(self) -> str:
        """ROI 最高的策略名（仅供研究，不承诺未来）。"""
        if not self.strategies:
            return "random"
        return max(self.strategies, key=lambda k: self.strategies[k].roi_total)

    def to_dict(self) -> dict:
        return {
            "periods": self.periods,
            "strategies": {k: _perf_to_dict(v) for k, v in self.strategies.items()},
            "best_strategy": self.best_strategy(),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = [f"📈 彩票策略回测（最近 {self.periods} 期）"]
        for name, perf in self.strategies.items():
            label = STRATEGY_NAMES.get(name, name)
            lines.append(
                f"· {label}：ROI {perf.roi_total:+.1f}% | 命中率 {perf.win_rate * 100:.1f}% "
                f"| 样本外 {perf.roi_oos:+.1f}%"
            )
        lines.append(f"· 随机基准 ROI 均值：{self._baseline_mean():+.1f}%")
        lines.append(f"· 最高 ROI 策略：{STRATEGY_NAMES.get(self.best_strategy(), self.best_strategy())}")
        lines.append("· 说明：历史回测不代表未来，不构成盈利保证。")
        return "\n".join(lines)

    def _baseline_mean(self) -> float:
        vals = [v.baseline_roi_mean for v in self.strategies.values() if v.baseline_roi_mean]
        return sum(vals) / len(vals) if vals else 0.0


def _perf_to_dict(perf: PerformanceReport) -> dict:
    return {
        "method": perf.method,
        "n_bets": perf.n_bets_total,
        "roi_total": round(perf.roi_total, 2),
        "roi_oos": round(perf.roi_oos, 2),
        "win_rate": round(perf.win_rate, 4),
        "baseline_roi_mean": round(perf.baseline_roi_mean, 2),
        "better_than_random": perf.better_than_random,
        "conclusion": perf.conclusion(),
    }


def _run_random(draws, periods: int = 100, seed: int = 42) -> PerformanceReport:
    """随机策略回测（与热/冷/均衡同口径）。"""
    data = draws[-periods:] if len(draws) > periods else draws
    if len(data) < 4:
        return PerformanceReport(method="random")
    rng = random.Random(seed)
    cost_total = revenue_total = wins = 0
    records = []
    equity = 0.0
    for i in range(3, len(data)):
        rec = {"front": sorted(rng.sample(range(1, 36), 5)),
               "back": sorted(rng.sample(range(1, 13), 2))}
        actual = data[i]
        fh = len(set(rec["front"]) & set(actual.front))
        bh = len(set(rec["back"]) & set(actual.back))
        _, amount = _grade(fh, bh, DLT_PRIZES)
        cost_total += 2.0
        revenue_total += amount
        equity += amount - 2.0
        if amount > 0:
            wins += 1
    roi = (revenue_total - cost_total) / cost_total * 100 if cost_total else 0.0
    return PerformanceReport(
        method="random",
        n_bets_total=len(data) - 3,
        n_bets_train=0,
        n_bets_oos=len(data) - 3,
        roi_total=roi,
        roi_train=0.0,
        roi_oos=roi,
        win_rate=wins / max(1, len(data) - 3),
        avg_front_hit=0.0,
        max_drawdown=0.0,
        baseline_roi_mean=roi,  # 随机策略以自身为基准（对照意义）
        baseline_roi_p5=roi,
        baseline_roi_p95=roi,
        records=[],
    )


class StrategyBacktester:
    """策略回测器。"""

    @staticmethod
    def _load_draws() -> list:
        from engine.data_center_v2 import DataSourceManager
        mgr = DataSourceManager.from_project("dlt")
        return mgr.load()

    @classmethod
    def run(cls, draws: Optional[list] = None, periods: int = 100,
            methods: Optional[List[str]] = None, seed: int = 42) -> StrategyReport:
        """运行多策略回测。"""
        draws = draws if draws is not None else cls._load_draws()
        methods = methods or STRATEGY_METHODS
        report = StrategyReport(periods=min(periods, len(draws)))

        data = draws[-periods:] if len(draws) > periods else draws
        for method in methods:
            if method == "random":
                perf = _run_random(data, periods=periods, seed=seed)
            else:
                perf = run_backtest_with_evaluation(data, method=method, seed=seed)
            report.strategies[method] = perf
        return report


def run_strategy_backtest(draws: Optional[list] = None, periods: int = 100,
                          methods: Optional[List[str]] = None, seed: int = 42) -> StrategyReport:
    """便捷函数：策略回测。"""
    return StrategyBacktester.run(draws, periods, methods, seed)
