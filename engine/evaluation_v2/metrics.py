"""evaluation_v2 - 性能报告。

对一次回测计算完整性能指标，并按样本内/样本外划分分别报告，
同时提供与随机基准的对比结论。

禁止任何「诱导中奖概率」表达——报告只呈现统计事实与随机性说明。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .baseline import RandomBaseline, DLT_PRIZES, _grade
from .split import temporal_split


@dataclass
class BacktestRecord:
    """一期回测记录。"""

    issue: str
    recommended: str
    actual: str
    front_hit: int
    back_hit: int
    prize_name: Optional[str]
    amount: float
    equity: float
    is_oos: bool = False  # 是否样本外（out-of-sample）


def _recommend(draws, method: str):
    """生成推荐号码。与 desktop/stats.recommendation 保持一致（避免循环依赖）。"""
    from collections import Counter

    front_n, back_n = 5, 2
    fc = Counter(n for d in draws for n in d.front)
    bc = Counter(n for d in draws for n in d.back)
    if method == "hot":
        f = [n for n, _ in fc.most_common(front_n)]
        b = [n for n, _ in bc.most_common(back_n)]
    elif method == "cold":
        f = sorted(fc, key=lambda n: (fc[n], n))[:front_n]
        b = sorted(bc, key=lambda n: (bc[n], n))[:back_n]
    else:  # balanced
        cand_f = sorted(set(range(1, 36)))
        f = cand_f[::3][:front_n] if cand_f else [1, 2, 3, 4, 5]
        b = sorted(set(range(1, 13)))[::6][:back_n] if back_n else []
        if len(b) < back_n:
            b = [1, 2]
    return {"front": sorted(f)[:front_n], "back": sorted(b)[:back_n]}


@dataclass
class PerformanceReport:
    """回测性能报告。"""

    method: str
    n_bets_total: int = 0
    n_bets_train: int = 0
    n_bets_oos: int = 0
    roi_total: float = 0.0
    roi_train: float = 0.0
    roi_oos: float = 0.0
    win_rate: float = 0.0
    avg_front_hit: float = 0.0
    max_drawdown: float = 0.0
    baseline_roi_mean: float = 0.0
    baseline_roi_p5: float = 0.0
    baseline_roi_p95: float = 0.0
    records: List[BacktestRecord] = field(default_factory=list)

    @property
    def excess_roi(self) -> float:
        """超额收益：策略 ROI - 随机基准 ROI。"""
        return self.roi_total - self.baseline_roi_mean

    @property
    def better_than_random(self) -> bool:
        """是否高于随机基准 95% 区间上界（统计意义上的优势）。"""
        return self.roi_total > self.baseline_roi_p95

    def conclusion(self) -> str:
        """结论文案（诚实、无诱导）。"""
        lines = []
        if self.n_bets_oos > 0:
            lines.append(
                f"样本内(前70%) ROI {self.roi_train:+.1f}% / 样本外(后30%) ROI {self.roi_oos:+.1f}%"
            )
        lines.append(
            f"随机基准 ROI 均值 {self.baseline_roi_mean:+.1f}% (90%区间 {self.baseline_roi_p5:+.1f}%~{self.baseline_roi_p95:+.1f}%)"
        )
        if self.better_than_random:
            lines.append("本策略收益高于随机基准 90% 区间上界，但样本有限，仍需谨慎。")
        else:
            lines.append("本策略收益未显著优于随机选号，统计上无优势。")
        lines.append("彩票开奖为独立随机事件，历史回测不代表未来。")
        return "\n".join(lines)


def run_backtest_with_evaluation(
    draws,
    method: str = "hot",
    train_ratio: float = 0.7,
    n_simulations: int = 50,
    seed: Optional[int] = 42,
) -> PerformanceReport:
    """运行完整回测 + 随机基准，输出性能报告。

    Args:
        draws: 按时间升序的开奖记录。
        method: hot / cold / balanced。
        train_ratio: 训练集占比。
        n_simulations: 随机基准模拟次数。

    Returns:
        PerformanceReport（含逐期记录）。
    """
    if len(draws) < 5:
        return PerformanceReport(method=method)

    train, valid = temporal_split(draws, train_ratio)
    n_train = len(train)

    records: List[BacktestRecord] = []
    equity = 0.0
    cost_total = 0.0
    revenue_total = 0.0
    wins = 0
    hit_counts: List[int] = []

    # Walk-forward：从第 3 期起，用前面所有期做推荐
    for i in range(3, len(draws)):
        hist = draws[:i]
        rec = _recommend(hist, method)
        actual = draws[i]
        fh = len(set(rec["front"]) & set(actual.front))
        bh = len(set(rec["back"]) & set(actual.back))
        _, amount = _grade(fh, bh)
        cost_total += 2.0
        revenue_total += amount
        equity += amount - 2.0
        if amount > 0:
            wins += 1
        hit_counts.append(fh)
        records.append(
            BacktestRecord(
                issue=actual.number,
                recommended=" ".join(f"{n:02d}" for n in rec["front"]),
                actual=actual.format_front(),
                front_hit=fh,
                back_hit=bh,
                prize_name=_grade(fh, bh)[0],
                amount=amount,
                equity=equity,
                is_oos=i >= n_train,
            )
        )

    n = len(records)
    roi_total = (revenue_total - cost_total) / cost_total * 100 if cost_total else 0.0

    # 样本内/外分开
    train_recs = [r for r in records if not r.is_oos]
    oos_recs = [r for r in records if r.is_oos]

    def _roi(recs):
        if not recs:
            return 0.0
        rev = sum(r.amount for r in recs)
        cost = len(recs) * 2.0
        return (rev - cost) / cost * 100 if cost else 0.0

    # 随机基准（在验证集/全部数据上）
    baseline = RandomBaseline(n_simulations=n_simulations, seed=seed)
    baseline_result = baseline.evaluate(valid if valid else draws)

    # 最大回撤
    equities = [0.0] + [r.equity for r in records]
    peak = equities[0]
    max_dd = 0.0
    for v in equities:
        if v > peak:
            peak = v
        dd = peak - v
        if dd > max_dd:
            max_dd = dd

    report = PerformanceReport(
        method=method,
        n_bets_total=n,
        n_bets_train=len(train_recs),
        n_bets_oos=len(oos_recs),
        roi_total=roi_total,
        roi_train=_roi(train_recs),
        roi_oos=_roi(oos_recs),
        win_rate=wins / n if n else 0.0,
        avg_front_hit=sum(hit_counts) / len(hit_counts) if hit_counts else 0.0,
        max_drawdown=max_dd,
        baseline_roi_mean=baseline_result["roi_mean"],
        baseline_roi_p5=baseline_result["roi_p5"],
        baseline_roi_p95=baseline_result["roi_p95"],
        records=records,
    )
    return report
