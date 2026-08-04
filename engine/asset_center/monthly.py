"""asset_center.monthly - 月度复盘报告（v4.6 P5 资产中心 2.0）。

每月：购买 / 中奖 / 净收益 —— 保持诚实（彩票长期负期望）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DISCLAIMER = "复盘仅陈述历史事实。彩票长期为负期望，理性购彩。"


@dataclass
class MonthlySummary:
    """一个月度复盘。"""

    year: int = 0
    month: int = 0
    investment: float = 0.0
    winnings: float = 0.0
    ticket_count: int = 0
    win_count: int = 0

    @property
    def net(self) -> float:
        return self.winnings - self.investment

    @property
    def label(self) -> str:
        return f"{self.year}年{self.month}月"

    def to_dict(self) -> dict:
        return {"year": self.year, "month": self.month,
                "investment": round(self.investment, 2),
                "winnings": round(self.winnings, 2),
                "net": round(self.net, 2),
                "ticket_count": self.ticket_count,
                "win_count": self.win_count}

    def text(self) -> str:
        return (f"{self.label}：购买 ¥{self.investment:,.0f} · "
                f"中奖 ¥{self.winnings:,.0f} · 净收益 ¥{self.net:,.0f}")


@dataclass
class MonthlyReport:
    """多个月度复盘报告。"""

    items: List[MonthlySummary] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def total_net(self) -> float:
        return sum(i.net for i in self.items)

    def latest(self) -> Optional[MonthlySummary]:
        return self.items[-1] if self.items else None

    def to_dict(self) -> dict:
        return {"items": [i.to_dict() for i in self.items],
                "total_net": round(self.total_net, 2)}

    def to_text(self) -> str:
        lines = ["📅 月度复盘报告"]
        for it in self.items[-6:]:
            lines.append("· " + it.text())
        lines.append(f"· 累计净收益：¥{self.total_net:,.0f}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class MonthlyReportBuilder:
    """构建月度复盘。"""

    @classmethod
    def build(cls, tickets: List[dict],
              months: Optional[int] = None) -> MonthlyReport:
        """按购买月份聚合月度复盘。months=最近 N 个月（默认全部）。"""
        from collections import defaultdict

        # 月份 -> [投资, 中奖, 票数, 中奖次数]
        agg = defaultdict(lambda: [0.0, 0.0, 0, 0])
        for t in tickets:
            key = (t.get("buy_date") or t.get("saved_at", ""))[:7]
            if len(key) != 7:
                continue
            try:
                year, month = int(key[:4]), int(key[5:7])
            except (ValueError, IndexError):
                continue
            cost = float(t.get("cost", 2.0))
            won, amount = cls._win_of(t)
            a = agg[(year, month)]
            a[0] += cost
            a[1] += amount
            a[2] += 1
            if won:
                a[3] += 1

        items = []
        for (year, month), a in sorted(agg.items()):
            items.append(MonthlySummary(year=year, month=month,
                                        investment=a[0], winnings=a[1],
                                        ticket_count=a[2], win_count=a[3]))
        if months:
            items = items[-months:]
        return MonthlyReport(items=items)

    @staticmethod
    def _win_of(t: dict) -> tuple:
        """单张票据是否中奖及金额。"""
        try:
            from engine.lottery_intent.draw_matcher import DrawResultMatcher
            from engine.lottery_intent.prize_calculator import PrizeCalculator
            match = DrawResultMatcher().match(
                list(t.get("front", [])), list(t.get("back", [])),
                lottery=t.get("lottery", "dlt"),
                draw_date=t.get("draw_date", ""))
            if not match.draw:
                return False, 0.0
            pr = PrizeCalculator.calculate(match.front_hits, match.back_hits,
                                           t.get("lottery", "dlt"))
            return (True, pr.amount) if pr.won else (False, 0.0)
        except Exception:
            return False, 0.0


def build_monthly_report(tickets: List[dict],
                         months: Optional[int] = None) -> MonthlyReport:
    """便捷函数。"""
    return MonthlyReportBuilder.build(tickets, months)
