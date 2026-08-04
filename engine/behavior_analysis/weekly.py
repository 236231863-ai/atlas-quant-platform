"""behavior_analysis.weekly - 每周彩票报告（v4.7 P6 留存设计）。

内容：本周购买次数 / 中奖情况 / 投入 / 风险提醒。
目标：让用户每周回来查看。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

DISCLAIMER = "彩票开奖结果具有随机性，理性购彩。"


@dataclass
class WeeklyReport:
    """一周彩票报告。"""

    week_start: str = ""
    week_end: str = ""
    ticket_count: int = 0
    investment: float = 0.0
    winnings: float = 0.0
    win_count: int = 0
    risk_note: str = ""

    @property
    def net(self) -> float:
        return self.winnings - self.investment

    def to_dict(self) -> dict:
        return {"week_start": self.week_start, "week_end": self.week_end,
                "ticket_count": self.ticket_count,
                "investment": round(self.investment, 2),
                "winnings": round(self.winnings, 2),
                "net": round(self.net, 2), "win_count": self.win_count,
                "risk_note": self.risk_note}

    def summary_text(self) -> str:
        lines = [f"📅 本周彩票报告（{self.week_start} ~ {self.week_end}）"]
        lines.append(f"· 购买：{self.ticket_count} 次 · 投入 ¥{self.investment:,.0f}")
        lines.append(f"· 中奖：{self.win_count} 次 · ¥{self.winnings:,.0f} · 净收益 ¥{self.net:,.0f}")
        if self.risk_note:
            lines.append(f"· ⚠️ {self.risk_note}")
        lines.append(f"· {DISCLAIMER}")
        return "\n".join(lines)


class WeeklyReportBuilder:
    """每周报告构建器。"""

    @staticmethod
    def _week_bounds(now: Optional[date] = None, offset: int = 0) -> tuple:
        """当前（或偏移）周的周一~周日。"""
        now = now or date.today()
        monday = now - timedelta(days=now.weekday()) + timedelta(weeks=offset)
        return monday.isoformat(), (monday + timedelta(days=6)).isoformat()

    @classmethod
    def build(cls, tickets: List[dict], now: Optional[date] = None,
              offset: int = 0) -> WeeklyReport:
        """本周（或偏移周）报告。"""
        start, end = cls._week_bounds(now, offset)
        rep = WeeklyReport(week_start=start, week_end=end)
        week_tickets = [t for t in tickets
                        if start <= (t.get("buy_date") or t.get("saved_at", ""))[:10] <= end]
        if not week_tickets:
            rep.risk_note = "本周暂无购彩记录"
            return rep
        rep.ticket_count = len(week_tickets)
        rep.investment = sum(float(t.get("cost", 2.0)) for t in week_tickets)
        for t in week_tickets:
            level, amount = cls._win_of(t)
            if level:
                rep.win_count += 1
                rep.winnings += amount
        rep.risk_note = cls._risk_note(rep)
        return rep

    @staticmethod
    def _win_of(t: dict) -> tuple:
        try:
            from engine.lottery_intent.draw_matcher import DrawResultMatcher
            from engine.lottery_intent.prize_calculator import PrizeCalculator
            match = DrawResultMatcher().match(
                list(t.get("front", [])), list(t.get("back", [])),
                lottery=t.get("lottery", "dlt"), draw_date=t.get("draw_date", ""))
            if not match.draw:
                return None, 0.0
            pr = PrizeCalculator.calculate(match.front_hits, match.back_hits,
                                           t.get("lottery", "dlt"))
            return ("win", pr.amount) if pr.won else (None, 0.0)
        except Exception:
            return None, 0.0

    @staticmethod
    def _risk_note(rep: WeeklyReport) -> str:
        if rep.ticket_count == 0:
            return ""
        notes = []
        if rep.ticket_count > 10:
            notes.append(f"本周购买较频繁（{rep.ticket_count} 次）")
        if rep.investment > 100:
            notes.append(f"本周投入偏高（¥{rep.investment:,.0f}）")
        if rep.win_count == 0 and rep.ticket_count >= 3:
            notes.append("本周未中奖，注意控制投入")
        return "；".join(notes)


def build_weekly_report(tickets: List[dict], now: Optional[date] = None,
                        offset: int = 0) -> WeeklyReport:
    """便捷函数。"""
    return WeeklyReportBuilder.build(tickets, now, offset)
