"""portfolio - 投注组合分析器（v3.9.0 Phase 5）。

指标：
  1. 号码重复率   出现≥2次的号码 / 不同号码
  2. 组合相关性   注对之间前区重叠度（Jaccard）
  3. 覆盖范围     使用号码数 / 号码池
  4. 集中风险     高频号码集中度

输出 PortfolioReport + 优化建议。

重要：只能优化组合结构，不能保证中奖。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from engine.lottery_quant.structure.analyzer import StructureAnalyzer

DISCLAIMER = "优化建议仅改善组合结构，不能保证中奖。开奖结果具有随机性。"

# 彩种前区号码池大小
FRONT_POOL = {"dlt": 35, "ssq": 33}


@dataclass
class PortfolioReport:
    """组合分析报告。"""

    lottery: str = "dlt"
    lottery_name: str = "大乐透"
    note_count: int = 0
    duplicate_ratio: float = 0.0
    correlation: float = 0.0
    coverage: float = 0.0
    concentration: float = 0.0
    risk_assessment: str = "低"
    suggestions: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "note_count": self.note_count,
            "duplicate_ratio": round(self.duplicate_ratio, 4),
            "correlation": round(self.correlation, 4),
            "coverage": round(self.coverage, 4),
            "concentration": round(self.concentration, 4),
            "risk_assessment": self.risk_assessment,
            "suggestions": list(self.suggestions),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = [f"🧩 投注组合分析（{self.lottery_name}）"]
        lines.append(f"· 投注注数：{self.note_count} 注")
        lines.append(f"· 号码重复率：{self.duplicate_ratio * 100:.0f}%")
        lines.append(f"· 组合相关性：{self.correlation * 100:.0f}%")
        lines.append(f"· 覆盖范围：{self.coverage * 100:.0f}%（号码池 {FRONT_POOL.get(self.lottery, 35)}）")
        lines.append(f"· 集中度：{self.concentration * 100:.0f}%")
        lines.append(f"· 集中风险：{self.risk_assessment}")
        if self.suggestions:
            lines.append("· 优化建议：")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class PortfolioAnalyzer:
    """投注组合分析器。"""

    @staticmethod
    def _front_sets(tickets: List[dict]) -> List[set]:
        return [set(t.get("front", [])) for t in tickets if t.get("front")]

    @classmethod
    def correlation(cls, tickets: List[dict]) -> float:
        """组合相关性：注对前区 Jaccard 重叠度平均。"""
        sets = cls._front_sets(tickets)
        if len(sets) < 2:
            return 0.0
        total = 0.0
        pairs = 0
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                inter = len(sets[i] & sets[j])
                union = len(sets[i] | sets[j])
                total += inter / union if union else 0.0
                pairs += 1
        return total / pairs if pairs else 0.0

    @classmethod
    def coverage(cls, tickets: List[dict], lottery: str = "dlt") -> float:
        """覆盖范围：使用的不同前区号码 / 号码池。"""
        used = set()
        for t in tickets:
            used.update(t.get("front", []))
        pool = FRONT_POOL.get(lottery, 35)
        return len(used) / pool if pool else 0.0

    @classmethod
    def concentration(cls, tickets: List[dict]) -> float:
        """集中风险：前区号码出现次数 top 集中度。"""
        all_front = []
        for t in tickets:
            all_front.extend(t.get("front", []))
        if not all_front:
            return 0.0
        counter = Counter(all_front)
        total = len(all_front)
        # 最常用号码出现占比 × 出现频率最高 3 个号占比
        top3 = sum(v for _, v in counter.most_common(3))
        return top3 / total if total else 0.0

    @staticmethod
    def _assess(dup: float, corr: float, conc: float) -> str:
        if dup > 0.4 or corr > 0.45 or conc > 0.35:
            return "高"
        if dup > 0.2 or corr > 0.25 or conc > 0.2:
            return "中"
        return "低"

    @staticmethod
    def _suggestions(dup: float, corr: float, cov: float, conc: float) -> List[str]:
        tips = []
        if dup > 0.3:
            tips.append("重复率偏高：建议增加号码多样性，减少重复号码")
        if corr > 0.4:
            tips.append("组合相关性偏高：建议分散各注号码，避免高度重叠")
        if cov < 0.25:
            tips.append(f"覆盖范围偏低：建议扩展号码池覆盖（当前 {cov * 100:.0f}%）")
        if conc > 0.3:
            tips.append("集中度偏高：建议均衡高频/低频号码分布")
        if not tips:
            tips.append("结构较均衡：可保持当前组合，注意控制投入预算")
        tips.append("结构优化不改变中奖概率，请理性购彩")
        return tips

    @classmethod
    def analyze(cls, tickets: List[dict], lottery: str = "dlt") -> PortfolioReport:
        """分析多注组合。"""
        dup = StructureAnalyzer.duplicate_ratio(tickets)
        corr = cls.correlation(tickets)
        cov = cls.coverage(tickets, lottery)
        conc = cls.concentration(tickets)
        return PortfolioReport(
            lottery=lottery,
            lottery_name="大乐透" if lottery == "dlt" else "双色球",
            note_count=len(tickets),
            duplicate_ratio=dup,
            correlation=corr,
            coverage=cov,
            concentration=conc,
            risk_assessment=cls._assess(dup, corr, conc),
            suggestions=cls._suggestions(dup, corr, cov, conc),
        )


def analyze_portfolio(tickets: List[dict], lottery: str = "dlt") -> PortfolioReport:
    """便捷函数：组合分析。"""
    return PortfolioAnalyzer.analyze(tickets, lottery)
