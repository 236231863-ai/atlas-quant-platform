"""annual_report - 年度彩票报告（v4.2 Phase 4 数据导出）。

用户拥有自己的数据。PDF 年度报告：
  购买次数 / 投入金额 / 中奖次数 / 最高奖金 / 购彩习惯

红线：年度总结只陈述已发生事实，不预测、不诱导。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

DISCLAIMER = "本报告为个人购彩数据总结，不构成任何购彩建议。彩票开奖结果具有随机性。"

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class AnnualReport:
    """年度彩票报告。"""

    year: int = date.today().year
    ticket_count: int = 0
    total_investment: float = 0.0
    total_winnings: float = 0.0
    win_count: int = 0
    max_win: float = 0.0
    favorite_lotteries: List[str] = field(default_factory=list)
    monthly_trend: dict = field(default_factory=dict)
    purchase_days: int = 0
    first_ticket_date: str = ""
    last_ticket_date: str = ""
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "ticket_count": self.ticket_count,
            "total_investment": round(self.total_investment, 2),
            "total_winnings": round(self.total_winnings, 2),
            "win_count": self.win_count,
            "max_win": round(self.max_win, 2),
            "favorite_lotteries": list(self.favorite_lotteries),
            "monthly_trend": {k: round(v, 2) for k, v in self.monthly_trend.items()},
            "purchase_days": self.purchase_days,
            "first_ticket_date": self.first_ticket_date,
            "last_ticket_date": self.last_ticket_date,
            "disclaimer": self.disclaimer,
        }

    def summary_lines(self) -> List[str]:
        """年度总结文本行（PDF 渲染用）。"""
        lines = [
            f"**{self.year} 年彩票年度总结**",
            "",
            f"· 购买次数：{self.ticket_count} 次",
            f"· 投入金额：¥{self.total_investment:,.0f}",
            f"· 中奖次数：{self.win_count} 次",
            f"· 中奖金额：¥{self.total_winnings:,.0f}",
            f"· 最高奖金：¥{self.max_win:,.0f}",
            f"· 购买周期：{self.purchase_days} 个活跃日",
        ]
        if self.favorite_lotteries:
            lines.append("· 常购彩种：" + " / ".join(self.favorite_lotteries))
        if self.monthly_trend:
            lines.append("· 每月投入：" + "，".join(
                f"{m}月 ¥{v:,.0f}" for m, v in sorted(self.monthly_trend.items())))
        if self.first_ticket_date and self.last_ticket_date:
            lines.append(f"· 首次购买：{self.first_ticket_date} → 最近：{self.last_ticket_date}")
        if self.total_investment > 0:
            net = self.total_winnings - self.total_investment
            lines.append(f"· 年度净收益：¥{net:,.0f}")
            if net < 0:
                lines.append("  （彩票为负期望游戏，理性看待投入）")
        lines.append(f"· {self.disclaimer}")
        return lines

    def summary_text(self) -> str:
        return "\n".join(self.summary_lines())

    def export_pdf(self, path: str) -> str:
        """导出为 PDF。"""
        from engine.export import PDFExporter
        return PDFExporter.export_report(f"Atlas 年度报告 {self.year}", self.summary_lines(), path)


class AnnualReportEngine:
    """年度报告引擎。"""

    @classmethod
    def _name(cls, lottery: str) -> str:
        return LOTTERY_NAMES.get(lottery, lottery)

    @classmethod
    def build(cls, tickets: List[dict], year: Optional[int] = None) -> AnnualReport:
        """构建年度报告（筛选指定年份票据）。"""
        year = year or date.today().year
        rep = AnnualReport(year=year)

        year_tickets = []
        for t in tickets:
            d = t.get("buy_date") or t.get("saved_at", "")[:10]
            if d and len(d) == 10 and d.startswith(f"{year}-"):
                year_tickets.append(t)

        rep.ticket_count = len(year_tickets)
        if not year_tickets:
            return rep

        rep.total_investment = sum(float(t.get("cost", 2.0)) for t in year_tickets)

        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator
        matcher = DrawResultMatcher()

        monthly = Counter()
        buy_dates = set()
        for t in year_tickets:
            lottery = t.get("lottery", "dlt")
            front = list(t.get("front", []))
            back = list(t.get("back", []))
            d = t.get("buy_date") or t.get("saved_at", "")[:10]
            if d:
                buy_dates.add(d)
                monthly[d[5:7]] += float(t.get("cost", 2.0))
            try:
                match = matcher.match(front, back, lottery=lottery,
                                      purchase_date=d or None,
                                      draw_date=t.get("draw_date", "") or None)
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, lottery)
                    if pr.won:
                        rep.total_winnings += pr.amount
                        rep.win_count += 1
                        rep.max_win = max(rep.max_win, pr.amount)
            except Exception:
                continue

        rep.purchase_days = len(buy_dates)
        rep.monthly_trend = {k: round(v, 2) for k, v in monthly.items()}
        if buy_dates:
            rep.first_ticket_date = min(buy_dates)
            rep.last_ticket_date = max(buy_dates)

        dist = Counter(cls._name(t.get("lottery", "dlt")) for t in year_tickets)
        rep.favorite_lotteries = [name for name, _ in dist.most_common(2)]
        return rep

    @classmethod
    def build_from_manager(cls, year: Optional[int] = None) -> AnnualReport:
        """从 TicketManager 读取票据构建年度报告。"""
        from engine.ticket_system import TicketManager
        tickets = [t.__dict__ for t in TicketManager().list_all()]
        return cls.build(tickets, year)


def annual_report(tickets: List[dict], year: Optional[int] = None) -> AnnualReport:
    """便捷函数：年度报告。"""
    return AnnualReportEngine.build(tickets, year)
