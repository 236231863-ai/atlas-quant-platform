"""profile_card.card - 个人彩票档案卡（v4.8 P4）。

类似个人财务档案：彩票年龄/购买次数/累计投入/中奖/最佳中奖/连续周期/风险等级。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

DISCLAIMER = "档案仅陈述历史事实。彩票开奖结果具有随机性。"


@dataclass
class ProfileCard:
    """个人彩票档案卡。"""

    lottery_age_days: int = 0
    total_tickets: int = 0
    total_investment: float = 0.0
    total_winnings: float = 0.0
    best_win: float = 0.0
    best_win_date: str = ""
    consecutive_periods: int = 0       # 连续购彩周期（月）
    risk_level: str = "A"
    favorite_lottery: str = ""
    first_bet_date: str = ""
    last_bet_date: str = ""
    disclaimer: str = DISCLAIMER

    @property
    def net(self) -> float:
        return self.total_winnings - self.total_investment

    def to_dict(self) -> dict:
        return {"lottery_age_days": self.lottery_age_days,
                "total_tickets": self.total_tickets,
                "total_investment": round(self.total_investment, 2),
                "total_winnings": round(self.total_winnings, 2),
                "best_win": round(self.best_win, 2),
                "best_win_date": self.best_win_date,
                "consecutive_periods": self.consecutive_periods,
                "risk_level": self.risk_level,
                "favorite_lottery": self.favorite_lottery,
                "first_bet_date": self.first_bet_date,
                "last_bet_date": self.last_bet_date,
                "net": round(self.net, 2)}

    def summary_text(self) -> str:
        lines = ["👤 我的彩票档案卡"]
        lines.append(f"· 彩票年龄：{self.lottery_age_days} 天（{self.first_bet_date} 起）")
        lines.append(f"· 累计购买：{self.total_tickets} 次 · 投入 ¥{self.total_investment:,.0f}")
        lines.append(f"· 累计中奖：¥{self.total_winnings:,.0f} · 最佳中奖 ¥{self.best_win:,.0f}")
        lines.append(f"· 连续购彩：{self.consecutive_periods} 个月 · 风险等级 {self.risk_level}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class ProfileCardBuilder:
    """档案卡构建器。"""

    @staticmethod
    def _risk_level(tickets_count: int, roi: float) -> str:
        """风险等级（基于投入规模与收益）。"""
        if tickets_count == 0:
            return "A"
        if roi <= -0.95:
            return "C"
        if roi <= -0.7:
            return "B"
        return "A"

    @classmethod
    def build(cls, tickets: List[dict]) -> ProfileCard:
        """从票据构建档案卡。"""
        card = ProfileCard()
        if not tickets:
            return card

        card.total_tickets = len(tickets)
        card.total_investment = sum(float(t.get("cost", 2.0)) for t in tickets)

        # 中奖统计
        win_amounts = []
        for t in tickets:
            try:
                from engine.lottery_intent.draw_matcher import DrawResultMatcher
                from engine.lottery_intent.prize_calculator import PrizeCalculator
                match = DrawResultMatcher().match(
                    list(t.get("front", [])), list(t.get("back", [])),
                    lottery=t.get("lottery", "dlt"), draw_date=t.get("draw_date", ""))
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits,
                                                   t.get("lottery", "dlt"))
                    if pr.won:
                        card.total_winnings += pr.amount
                        win_amounts.append((pr.amount, t.get("buy_date", "")))
            except Exception:
                pass
        if win_amounts:
            card.best_win, card.best_win_date = max(win_amounts)

        # 日期
        dates = sorted(t.get("buy_date") or t.get("saved_at", "")[:10] for t in tickets)
        dates = [d for d in dates if d]
        if dates:
            card.first_bet_date = dates[0]
            card.last_bet_date = dates[-1]
            try:
                f = datetime.strptime(dates[0], "%Y-%m-%d").date()
                card.lottery_age_days = (date.today() - f).days
            except ValueError:
                card.lottery_age_days = 0

        # 连续购彩周期（按购买月份跨度）
        months = {(t.get("buy_date") or t.get("saved_at", ""))[:7] for t in tickets
                  if (t.get("buy_date") or t.get("saved_at", ""))[:7]}
        card.consecutive_periods = len(months)

        # 常购彩种
        from collections import Counter
        cnt = Counter(t.get("lottery", "dlt") for t in tickets)
        if cnt:
            card.favorite_lottery = "大乐透" if cnt.most_common(1)[0][0] == "dlt" else "双色球"

        # 风险等级
        roi = (card.total_winnings - card.total_investment) / card.total_investment \
            if card.total_investment else 0.0
        card.risk_level = cls._risk_level(card.total_tickets, roi)
        return card


def build_profile_card(tickets: List[dict]) -> ProfileCard:
    """便捷函数。"""
    return ProfileCardBuilder.build(tickets)
