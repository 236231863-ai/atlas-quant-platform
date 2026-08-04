"""strategy_review.review - 策略复盘系统（v4.7 P4）。

分析用户过去行为（不预测）：
  倍投次数 / 随机选号次数 / 固定号码次数 / 重复号码比例 / 冷热策略使用
输出历史行为总结。

禁止：告诉用户下一期怎么买。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DISCLAIMER = "复盘仅陈述你的历史行为。彩票开奖结果具有随机性，任何策略不改变中奖概率。"


@dataclass
class StrategyReview:
    """历史行为总结。"""

    total_tickets: int = 0
    unique_combos: int = 0
    fixed_combo_count: int = 0          # 固定号码（重复出现 ≥2 次）
    random_count: int = 0               # 随机选号（只出现 1 次）
    repeat_ratio: float = 0.0           # 重复号码比例
    doubled_times: int = 0              # 倍投次数（同一组合 ≥2）
    hot_use: int = 0                    # 含热号的组合数
    cold_use: int = 0                   # 含冷号的组合数
    combos: Dict[str, int] = field(default_factory=dict)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {"total_tickets": self.total_tickets,
                "unique_combos": self.unique_combos,
                "fixed_combo_count": self.fixed_combo_count,
                "random_count": self.random_count,
                "repeat_ratio": round(self.repeat_ratio, 4),
                "doubled_times": self.doubled_times,
                "hot_use": self.hot_use, "cold_use": self.cold_use}

    def summary_text(self) -> str:
        lines = ["🔍 策略复盘（过去行为）"]
        lines.append(f"· 总投注：{self.total_tickets} 注 · 唯一组合：{self.unique_combos}")
        lines.append(f"· 固定号码：{self.fixed_combo_count} 注 · 随机选号：{self.random_count} 注")
        lines.append(f"· 重复比例：{self.repeat_ratio * 100:.0f}% · 倍投次数：{self.doubled_times}")
        lines.append(f"· 含热号组合：{self.hot_use} · 含冷号组合：{self.cold_use}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class StrategyReviewer:
    """策略复盘器。"""

    @classmethod
    def _combo_key(cls, t: dict) -> str:
        front = " ".join(f"{n:02d}" for n in t.get("front", []))
        back = " ".join(f"{n:02d}" for n in t.get("back", []))
        return f"{front}+{back}"

    @classmethod
    def _hot_cold(cls, tickets: List[dict], top_n: int = 8) -> tuple:
        """统计热号/冷号（出现频次最高/最低）。"""
        cnt = Counter()
        for t in tickets:
            for n in t.get("front", []) + t.get("back", []):
                cnt[n] += 1
        if not cnt:
            return set(), set()
        hot = {n for n, _ in cnt.most_common(top_n)}
        cold = {n for n, _ in cnt.most_common()[-top_n:]}
        return hot, cold

    @classmethod
    def build(cls, tickets: List[dict]) -> StrategyReview:
        """从历史票据构建策略复盘。"""
        review = StrategyReview()
        if not tickets:
            return review
        review.total_tickets = len(tickets)
        combos = Counter(cls._combo_key(t) for t in tickets)
        review.combos = dict(combos)
        review.unique_combos = len(combos)

        fixed = sum(1 for k, v in combos.items() if v >= 2)
        review.fixed_combo_count = fixed
        review.random_count = sum(1 for v in combos.values() if v == 1)
        review.doubled_times = sum(v - 1 for v in combos.values() if v >= 2)
        review.repeat_ratio = fixed / review.unique_combos if review.unique_combos else 0.0

        # 冷热策略使用
        hot, cold = cls._hot_cold(tickets)
        for t in tickets:
            nums = set(t.get("front", [])) | set(t.get("back", []))
            if nums & hot:
                review.hot_use += 1
            if nums & cold:
                review.cold_use += 1
        return review


def build_strategy_review(tickets: List[dict]) -> StrategyReview:
    """便捷函数。"""
    return StrategyReviewer.build(tickets)
