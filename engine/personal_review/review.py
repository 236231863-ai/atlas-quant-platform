"""personal_review - 历史投注复盘引擎（v4.0.0 Phase 3）。

读取历史票据，逐张匹配实际开奖，统计：
  - 总投入 / 总中奖 / 净收益 / 投入收益比
  - 中奖次数 / 中奖率
  - 购买趋势（每月投入）
  - 最高投入周期

输出 PersonalReviewReport。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

DISCLAIMER = "复盘数据基于历史开奖，不能预测未来开奖。彩票开奖结果具有随机性。"


@dataclass
class PersonalReviewReport:
    """个人复盘报告。"""

    total_tickets: int = 0
    total_investment: float = 0.0
    total_winnings: float = 0.0
    win_count: int = 0
    net_profit: float = 0.0
    roi: float = 0.0                # 投入收益比（净收益/投入）
    monthly_trend: dict = field(default_factory=dict)  # {YYYY-MM: 投入}
    peak_month: str = ""
    disclaimer: str = DISCLAIMER

    @property
    def win_rate(self) -> float:
        return self.win_count / self.total_tickets if self.total_tickets else 0.0

    def to_dict(self) -> dict:
        return {
            "total_tickets": self.total_tickets,
            "total_investment": round(self.total_investment, 2),
            "total_winnings": round(self.total_winnings, 2),
            "win_count": self.win_count,
            "win_rate": round(self.win_rate, 4),
            "net_profit": round(self.net_profit, 2),
            "roi": round(self.roi, 4),
            "monthly_trend": {k: round(v, 2) for k, v in self.monthly_trend.items()},
            "peak_month": self.peak_month,
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = ["📋 个人投注复盘"]
        lines.append(f"· 复盘票据：{self.total_tickets} 张")
        lines.append(f"· 总投入：¥{self.total_investment:,.0f}")
        lines.append(f"· 总中奖：¥{self.total_winnings:,.0f}")
        lines.append(f"· 净收益：¥{self.net_profit:,.0f}")
        lines.append(f"· 投入收益比：{self.roi * 100:+.1f}%")
        lines.append(f"· 中奖率：{self.win_rate * 100:.1f}%（{self.win_count} 次中奖）")
        if self.peak_month:
            lines.append(f"· 最高投入周期：{self.peak_month}")
        if self.net_profit < 0:
            lines.append("· 提示：当前投入大于回报，彩票为负期望游戏。")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class PersonalReviewEngine:
    """历史投注复盘引擎。"""

    @staticmethod
    def _parse_month(date_str: str) -> Optional[str]:
        """解析日期 → YYYY-MM。"""
        if not date_str:
            return None
        try:
            if len(date_str) == 10:
                return date_str[:7]
            if len(date_str) == 5:
                from datetime import date
                return f"{date.today().year}-{date_str[:2]}"
        except ValueError:
            return None
        return None

    @classmethod
    def review(cls, tickets: List[dict]) -> PersonalReviewReport:
        """复盘票据列表。

        tickets: [{"lottery", "front", "back", "buy_date", "draw_date", "cost"}]
        """
        report = PersonalReviewReport()
        if not tickets:
            return report

        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator

        matcher = DrawResultMatcher()
        monthly = Counter()

        for t in tickets:
            lottery = t.get("lottery", "dlt")
            front = list(t.get("front", []))
            back = list(t.get("back", []))
            cost = float(t.get("cost", 2.0))
            buy_date = t.get("buy_date", "") or t.get("saved_at", "")[:10]
            draw_date = t.get("draw_date", "")

            report.total_tickets += 1
            report.total_investment += cost

            # 月份趋势
            m = cls._parse_month(buy_date)
            if m:
                monthly[m] += cost

            # 匹配开奖（精确日期，防穿越）
            try:
                match = matcher.match(front, back, lottery=lottery,
                                      purchase_date=buy_date or None,
                                      draw_date=draw_date or None)
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, lottery)
                    if pr.won:
                        report.total_winnings += pr.amount
                        report.win_count += 1
            except Exception:
                continue

        report.net_profit = report.total_winnings - report.total_investment
        report.roi = report.net_profit / report.total_investment if report.total_investment else 0.0
        report.monthly_trend = dict(monthly)
        if monthly:
            report.peak_month = monthly.most_common(1)[0][0]
        return report

    @classmethod
    def review_from_manager(cls, ticket_manager=None) -> PersonalReviewReport:
        """从 TicketManager 读取票据复盘。"""
        if ticket_manager is None:
            from engine.ticket_system import TicketManager
            ticket_manager = TicketManager()
        tickets = [t.__dict__ for t in ticket_manager.list_all()]
        return cls.review(tickets)


def review_tickets(tickets: List[dict]) -> PersonalReviewReport:
    """便捷函数：复盘。"""
    return PersonalReviewEngine.review(tickets)
