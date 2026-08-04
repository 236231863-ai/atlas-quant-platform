"""behavior_analysis.score - 投注健康评分（v4.7 P2）。

不是中奖评分。维度：
  资金管理 40 / 投注纪律 30 / 复盘习惯 20 / 风险意识 10
输出健康分（0-100）+ 优势 + 风险提示。
禁止「中奖概率提升」。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

DISCLAIMER = "健康分反映购彩行为管理，不代表中奖能力。彩票开奖结果具有随机性。"


@dataclass
class ScoreDimension:
    """一个评分维度。"""

    name: str
    score: float
    max_score: float
    detail: str = ""

    @property
    def ratio(self) -> float:
        return self.score / self.max_score if self.max_score else 0.0

    def to_dict(self) -> dict:
        return {"name": self.name, "score": round(self.score, 1),
                "max": self.max_score, "detail": self.detail}


@dataclass
class BehaviorScore:
    """购彩健康评分。"""

    total: float = 0.0
    dimensions: List[ScoreDimension] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def level(self) -> str:
        if self.total >= 80:
            return "优秀"
        if self.total >= 60:
            return "良好"
        if self.total >= 40:
            return "需关注"
        return "高风险"

    def to_dict(self) -> dict:
        return {"total": round(self.total, 1), "level": self.level,
                "dimensions": [d.to_dict() for d in self.dimensions],
                "strengths": list(self.strengths), "risks": list(self.risks)}

    def summary_text(self) -> str:
        lines = ["🩺 购彩健康分"]
        lines.append(f"· 总分：{self.total:.0f}/100（{self.level}）")
        for d in self.dimensions:
            lines.append(f"  {d.name}：{d.score:.0f}/{d.max_score}")
        if self.strengths:
            lines.append("· 优势：")
            for s in self.strengths:
                lines.append(f"  ✅ {s}")
        if self.risks:
            lines.append("· 风险：")
            for r in self.risks:
                lines.append(f"  ⚠️ {r}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class BehaviorScoreBuilder:
    """投注健康评分器。"""

    # 资金管理 40：投入稳定性 + 无超支
    @classmethod
    def _fund_score(cls, rep) -> float:
        """资金管理（40 分）。"""
        score = 0.0
        # 有记录即基础分
        if rep.total_tickets > 0:
            score += 10
        # 投入稳定：平均每期在合理范围（<50 元）
        if rep.avg_per_bet <= 0:
            score += 10
        elif rep.avg_per_bet <= 20:
            score += 20
        elif rep.avg_per_bet <= 50:
            score += 12
        else:
            score += 4
        # 亏损率低（净收益/投入 不太差）
        if rep.roi >= -0.5:
            score += 10
        elif rep.roi >= -0.9:
            score += 6
        else:
            score += 2
        return min(score, 40)

    # 投注纪律 30：频率不过高 + 连续未中后未加码
    @classmethod
    def _discipline_score(cls, rep) -> float:
        score = 0.0
        if rep.total_tickets > 0:
            score += 5
        # 频率：每月 <=8 期较理性
        if rep.bet_frequency <= 0:
            score += 5
        elif rep.bet_frequency <= 8:
            score += 15
        elif rep.bet_frequency <= 20:
            score += 8
        else:
            score += 3
        # 最大亏损周期不长
        if rep.max_loss_streak <= 0:
            score += 10
        elif rep.max_loss_streak <= 5:
            score += 10
        elif rep.max_loss_streak <= 15:
            score += 6
        else:
            score += 2
        return min(score, 30)

    # 复盘习惯 20：有票据即有记录基础
    @classmethod
    def _review_score(cls, rep) -> float:
        score = 0.0
        if rep.total_tickets > 0:
            score += 10
        # 有跨月记录（说明持续使用复盘）
        if rep.bet_frequency > 0:
            score += 5
        if rep.total_tickets >= 5:
            score += 5
        elif rep.total_tickets >= 2:
            score += 3
        return min(score, 20)

    # 风险意识 10：接受负期望认知
    @classmethod
    def _risk_score(cls, rep) -> float:
        score = 0.0
        if rep.total_tickets > 0:
            score += 5
        # 有亏损经历且仍记录（理性面对）
        if rep.net < 0:
            score += 5
        elif rep.total_tickets >= 3:
            score += 3
        return min(score, 10)

    @classmethod
    def build(cls, rep) -> BehaviorScore:
        """从 UserBehaviorReport 构建健康分。"""
        dims = [
            ScoreDimension("资金管理", cls._fund_score(rep), 40),
            ScoreDimension("投注纪律", cls._discipline_score(rep), 30),
            ScoreDimension("复盘习惯", cls._review_score(rep), 20),
            ScoreDimension("风险意识", cls._risk_score(rep), 10),
        ]
        total = sum(d.score for d in dims)
        score = BehaviorScore(total=total, dimensions=dims)
        score.strengths = cls._strengths(rep)
        score.risks = cls._risks(rep)
        return score

    @staticmethod
    def _strengths(rep) -> List[str]:
        s = []
        if 0 < rep.avg_per_bet <= 20:
            s.append("每期投入稳定且克制")
        if 0 < rep.bet_frequency <= 8:
            s.append("购买频率较理性")
        if rep.win_count > 0:
            s.append("有中奖记录，坚持记录复盘")
        if not s:
            s.append("开始记录购彩行为本身是好的第一步")
        return s

    @staticmethod
    def _risks(rep) -> List[str]:
        r = []
        if rep.bet_frequency > 20:
            r.append("购买频率过高")
        if rep.max_loss_streak > 15:
            r.append("连续未中周期过长，需注意")
        if rep.avg_per_bet > 50:
            r.append("单期投入偏高")
        if rep.net < 0 and rep.total_tickets >= 3:
            r.append("长期亏损，建议重新评估预算")
        if not r and rep.total_tickets == 0:
            r.append("暂无投注记录")
        return r


def build_behavior_score(rep) -> BehaviorScore:
    """便捷函数。"""
    return BehaviorScoreBuilder.build(rep)
