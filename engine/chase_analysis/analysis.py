"""chase_analysis - 追号/遗漏分析。"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MissingInfo:
    """号码遗漏信息。"""

    number: int
    missing_issues: int = 0   # 连续未出期数
    total_count: int = 0      # 总出现次数

    def to_dict(self) -> dict:
        return {"number": self.number, "missing": self.missing_issues, "count": self.total_count}


class ChaseAnalysis:
    """追号分析：统计号码遗漏（非预测）。"""

    @staticmethod
    def missing_numbers(draws: list, front_range=(1, 35), top_k: int = 10) -> List[MissingInfo]:
        """统计每个前区号码的遗漏期数与总次数。

        遗漏 = 从最近一期往前，连续多少期未出现。
        """
        if not draws:
            return []
        # 号码 → 最后出现位置
        last_seen: Dict[int, int] = {}
        counts: Counter = Counter()
        n = len(draws)
        for i, d in enumerate(draws):
            for num in d.front:
                counts[num] += 1
                last_seen[num] = i  # 更新为最后出现
        info = []
        for num in range(front_range[0], front_range[1] + 1):
            miss = (n - 1 - last_seen[num]) if num in last_seen else n
            info.append(MissingInfo(number=num, missing_issues=miss, total_count=counts.get(num, 0)))
        # 按遗漏排序（最久未出在前）
        info.sort(key=lambda x: -x.missing_issues)
        return info[:top_k]

    @staticmethod
    def summary(draws: list, lottery: str = "dlt") -> str:
        """追号观察摘要（非预测声明）。"""
        top = ChaseAnalysis.missing_numbers(draws)
        lines = ["🔍 追号观察（遗漏统计）"]
        for m in top:
            lines.append(f"· 号码 {m.number:02d}：连续 {m.missing_issues} 期未出（累计 {m.total_count} 次）")
        lines.append("· 遗漏仅反映历史分布，彩票独立随机，不构成追号建议。")
        return "\n".join(lines)
