"""structure - 号码结构分析器（v3.9.0 Phase 2）。

指标：
  1. 奇偶比例       前区奇数/偶数
  2. 大小比例       前区大号(18-35)/小号(1-17)
  3. 三区分布       前区 1-12 / 13-24 / 25-35
  4. 和值           前区和值
  5. 跨度           前区 max-min
  6. 连号           连续号码对
  7. 重复号码       组合间重复号码占比
  8. 历史分布偏离度 号码频率 vs 历史均值

说明：组合评分反映结构均衡度，不是中奖概率。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DISCLAIMER = "结构分析仅反映号码组合的统计均衡度，不是中奖概率。开奖结果具有随机性。"


@dataclass
class StructureMetrics:
    """单注结构指标。"""

    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)
    odd_count: int = 0
    even_count: int = 0
    big_count: int = 0
    small_count: int = 0
    zone1: int = 0
    zone2: int = 0
    zone3: int = 0
    front_sum: int = 0
    span: int = 0
    consecutive_pairs: int = 0

    @property
    def odd_even_ratio(self) -> str:
        return f"{self.odd_count}:{self.even_count}"

    @property
    def big_small_ratio(self) -> str:
        return f"{self.big_count}:{self.small_count}"

    @property
    def zone_distribution(self) -> str:
        return f"{self.zone1}-{self.zone2}-{self.zone3}"

    def to_dict(self) -> dict:
        return {
            "front": list(self.front),
            "back": list(self.back),
            "odd_even": self.odd_even_ratio,
            "big_small": self.big_small_ratio,
            "zones": self.zone_distribution,
            "front_sum": self.front_sum,
            "span": self.span,
            "consecutive_pairs": self.consecutive_pairs,
        }


@dataclass
class CombinationScore:
    """组合评分结果。"""

    total_score: int = 0
    metrics: StructureMetrics = field(default_factory=StructureMetrics)
    assessment: str = ""
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "score": self.total_score,
            "metrics": self.metrics.to_dict(),
            "assessment": self.assessment,
            "disclaimer": self.disclaimer,
        }


class StructureAnalyzer:
    """号码结构分析器。"""

    # ---------- 指标 ----------
    @staticmethod
    def odd_even(front: List[int]) -> tuple:
        odd = sum(1 for n in front if n % 2 == 1)
        return odd, len(front) - odd

    @staticmethod
    def big_small(front: List[int]) -> tuple:
        big = sum(1 for n in front if n >= 18)
        return big, len(front) - big

    @staticmethod
    def zones(front: List[int]) -> tuple:
        z1 = sum(1 for n in front if 1 <= n <= 12)
        z2 = sum(1 for n in front if 13 <= n <= 24)
        z3 = sum(1 for n in front if 25 <= n <= 35)
        return z1, z2, z3

    @staticmethod
    def front_sum(front: List[int]) -> int:
        return sum(front)

    @staticmethod
    def span(front: List[int]) -> int:
        if not front:
            return 0
        return max(front) - min(front)

    @staticmethod
    def consecutive_pairs(front: List[int]) -> int:
        s = sorted(front)
        return sum(1 for a, b in zip(s, s[1:]) if b - a == 1)

    # ---------- 单注指标 ----------
    @classmethod
    def analyze_single(cls, front: List[int], back: Optional[List[int]] = None) -> StructureMetrics:
        f = sorted(front)
        odd, even = cls.odd_even(f)
        big, small = cls.big_small(f)
        z1, z2, z3 = cls.zones(f)
        return StructureMetrics(
            front=f, back=sorted(back or []),
            odd_count=odd, even_count=even,
            big_count=big, small_count=small,
            zone1=z1, zone2=z2, zone3=z3,
            front_sum=cls.front_sum(f), span=cls.span(f),
            consecutive_pairs=cls.consecutive_pairs(f),
        )

    # ---------- 重复号码 ----------
    @classmethod
    def duplicate_ratio(cls, tickets: List[dict]) -> float:
        """多注间号码重复率（0-1）：出现≥2次的号码数 / 总号码数。"""
        all_nums = []
        for t in tickets:
            all_nums.extend(t.get("front", []))
            all_nums.extend(t.get("back", []))
        if not all_nums:
            return 0.0
        from collections import Counter
        counter = Counter(all_nums)
        dup = sum(1 for v in counter.values() if v >= 2)
        return dup / len(counter) if counter else 0.0

    # ---------- 历史偏离度 ----------
    @classmethod
    def historical_deviation(cls, front: List[int], lottery: str = "dlt") -> float:
        """历史分布偏离度：号码频率与历史平均的归一化偏离（0-1）。"""
        try:
            from engine.data_center_v2 import DataSourceManager
            mgr = DataSourceManager.from_project(lottery)
            draws = mgr.load()
        except Exception:
            return 0.5
        if not draws:
            return 0.5
        freq = {}
        total_draws = len(draws)
        for d in draws:
            for n in d.front:
                freq[n] = freq.get(n, 0) + 1
        if not freq:
            return 0.5
        avg = total_draws / 35.0  # 前区 1-35 均匀期望
        if avg == 0:
            return 0.5
        deviations = []
        for n in front:
            f = freq.get(n, 0) / total_draws if total_draws else 0
            # 归一化：|f - avg_ratio| / avg_ratio，截断到 0-1
            d = min(1.0, abs(f * 35 - avg) / avg)
            deviations.append(d)
        return sum(deviations) / len(deviations) if deviations else 0.5

    # ---------- 评分 ----------
    @classmethod
    def score_single(cls, front: List[int], back: Optional[List[int]] = None,
                     lottery: str = "dlt") -> CombinationScore:
        """单注结构评分（0-100，结构均衡度）。"""
        m = cls.analyze_single(front, back)
        score = 0

        # 奇偶平衡：期望接近 (3,2) 或 (2,3)
        odd, even = m.odd_count, m.even_count
        if odd in (2, 3):
            score += 25
        elif odd in (1, 4):
            score += 15
        else:
            score += 5

        # 大小平衡
        big, small = m.big_count, m.small_count
        if big in (2, 3):
            score += 20
        elif big in (1, 4):
            score += 12
        else:
            score += 5

        # 三区分布：覆盖 ≥2 区
        zones_covered = sum(1 for z in (m.zone1, m.zone2, m.zone3) if z > 0)
        score += min(20, zones_covered * 8)

        # 和值适中（大乐透前区和值均值约 91，区间 60-120 常见）
        if 60 <= m.front_sum <= 120:
            score += 15
        elif 40 <= m.front_sum <= 140:
            score += 8
        else:
            score += 3

        # 跨度适中
        if 15 <= m.span <= 32:
            score += 12
        elif m.span > 10:
            score += 7
        else:
            score += 3

        # 连号少（0-1）
        score += max(0, 8 - m.consecutive_pairs * 4)

        score = min(100, score)

        # 评价
        if score >= 75:
            assessment = "结构均衡"
        elif score >= 55:
            assessment = "结构略偏"
        else:
            assessment = "结构偏集中"

        return CombinationScore(total_score=score, metrics=m, assessment=assessment)

    # ---------- 组合评分（多注）----------
    @classmethod
    def analyze(cls, tickets: List[dict], lottery: str = "dlt") -> CombinationScore:
        """分析多注组合：取平均结构评分 + 重复率。"""
        if not tickets:
            return CombinationScore()
        scores = [cls.score_single(t.get("front", []), t.get("back", []), lottery) for t in tickets]
        avg = int(sum(s.total_score for s in scores) / len(scores))
        dup = cls.duplicate_ratio(tickets)

        # 重复率扣分
        final = max(0, avg - int(dup * 30))

        if final >= 75:
            assessment = "结构均衡"
        elif final >= 55:
            assessment = "结构略偏"
        else:
            assessment = "结构偏集中"

        m = scores[0].metrics
        m.front = tickets[0].get("front", [])
        m.back = tickets[0].get("back", [])
        return CombinationScore(total_score=final, metrics=m,
                                assessment=f"{assessment}（重复率 {dup * 100:.0f}%）")


def analyze_combination(front: List[int], back: Optional[List[int]] = None,
                        lottery: str = "dlt") -> CombinationScore:
    """便捷函数：单注结构分析。"""
    return StructureAnalyzer.score_single(front, back, lottery)
