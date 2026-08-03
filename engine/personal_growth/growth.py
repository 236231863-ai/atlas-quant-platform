"""personal_growth - 个人成长引擎（v4.1 阶段4）。

指标：购彩历史 / 连续购买 / 连续中奖 / 月度报告 / 年度报告 / 个人趋势。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional

DISCLAIMER = "个人成长记录帮助你了解自己的购彩历程。彩票开奖结果具有随机性。"


@dataclass
class GrowthReport:
    """个人成长报告。"""

    total_days: int = 0                 # 有购彩记录的天数
    current_streak: int = 0             # 连续购买天数（当前）
    max_streak: int = 0                 # 历史最长连续购买
    consecutive_wins: int = 0           # 当前连续中奖期数
    monthly_summary: dict = field(default_factory=dict)   # {YYYY-MM: {spent, won}}
    annual_summary: dict = field(default_factory=dict)    # {YYYY: {spent, won, roi}}
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "total_days": self.total_days,
            "current_streak": self.current_streak,
            "max_streak": self.max_streak,
            "consecutive_wins": self.consecutive_wins,
            "monthly_summary": self.monthly_summary,
            "annual_summary": self.annual_summary,
            "disclaimer": self.disclaimer,
        }

    def annual_report_text(self, year: Optional[int] = None) -> str:
        """Atlas Annual Report 文本。"""
        year = year or date.today().year
        y = self.annual_summary.get(str(year), {})
        lines = [f"📅 Atlas 年度购彩报告（{year}）"]
        if not y:
            lines.append("· 该年度暂无购彩记录")
        else:
            spent = y.get("spent", 0)
            won = y.get("won", 0)
            roi = y.get("roi", 0)
            lines.append(f"· 累计投入：¥{spent:,.0f}")
            lines.append(f"· 累计中奖：¥{won:,.0f}")
            lines.append(f"· 净收益：¥{won - spent:,.0f}")
            lines.append(f"· 投入收益比：{roi * 100:+.1f}%")
        lines.append(f"· 连续购买最长：{self.max_streak} 天")
        lines.append(f"· 当前连续购买：{self.current_streak} 天")
        lines.append(f"· 连续中奖：{self.consecutive_wins} 期")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)

    def summary_text(self) -> str:
        lines = ["🌱 个人成长中心"]
        lines.append(f"· 购彩记录：{self.total_days} 天")
        lines.append(f"· 当前连续购买：{self.current_streak} 天 / 最长 {self.max_streak} 天")
        lines.append(f"· 连续中奖：{self.consecutive_wins} 期")
        months = sorted(self.monthly_summary.keys())
        if months:
            last = self.monthly_summary[months[-1]]
            lines.append(f"· 最近月份（{months[-1]}）：投入 ¥{last.get('spent', 0):,.0f} / 中奖 ¥{last.get('won', 0):,.0f}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class PersonalGrowthEngine:
    """个人成长引擎。"""

    @staticmethod
    def _parse_date(d: str) -> Optional[date]:
        if not d:
            return None
        try:
            if len(d) == 10:
                return date.fromisoformat(d)
            if len(d) == 5:
                return date.fromisoformat(f"{date.today().year}-{d}")
        except ValueError:
            return None
        return None

    @classmethod
    def _streaks(cls, dates: List[date]) -> tuple:
        """返回 (当前连续, 最长连续)。"""
        uniq = sorted(set(dates))
        if not uniq:
            return 0, 0
        # 当前连续：从今天向前数连续天
        today = date.today()
        current = 0
        day = today
        while day in set(uniq):
            current += 1
            day -= timedelta(days=1)
        # 最长连续
        max_streak = 1
        run = 1
        for a, b in zip(uniq, uniq[1:]):
            if (b - a).days == 1:
                run += 1
                max_streak = max(max_streak, run)
            else:
                run = 1
        return current, max_streak

    @classmethod
    def _consecutive_wins(cls, win_dates: List[date], today: date) -> int:
        """当前连续中奖期数（按票据结算日往前数）。"""
        if not win_dates:
            return 0
        uniq = sorted(set(win_dates))
        # 从最近的 win 日往回数（允许最近一次在未来）
        count = 0
        idx = len(uniq) - 1
        # 若最后一次中奖在未来（今天之前没有），从今天往前找连续
        while idx >= 0:
            prev = uniq[idx]
            if idx < len(uniq) - 1 and (uniq[idx + 1] - prev).days != 1:
                break
            count += 1
            idx -= 1
        return count

    @classmethod
    def build(cls, tickets: List[dict], lottery: str = "dlt") -> GrowthReport:
        """构建个人成长报告。"""
        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator

        matcher = DrawResultMatcher()
        buy_dates = []
        win_dates = []
        monthly = Counter()
        annual = {}

        for t in tickets:
            buy = cls._parse_date(t.get("buy_date") or t.get("saved_at", "")[:10])
            cost = float(t.get("cost", 2.0))
            if buy:
                buy_dates.append(buy)
                month_key = f"{buy.year}-{buy.month:02d}"
                monthly[(month_key, "spent")] += cost
                annual.setdefault(str(buy.year), {"spent": 0.0, "won": 0.0})
                annual[str(buy.year)]["spent"] += cost

            # 中奖结算
            draw = cls._parse_date(t.get("draw_date") or "")
            try:
                match = matcher.match(t.get("front", []), t.get("back", []),
                                      lottery=lottery,
                                      purchase_date=t.get("buy_date") or None,
                                      draw_date=t.get("draw_date") or None)
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, lottery)
                    if pr.won:
                        if draw:
                            win_dates.append(draw)
                        annual.setdefault(str(draw.year) if draw else str(date.today().year),
                                          {"spent": 0.0, "won": 0.0})
                        key = str(draw.year) if draw else str(date.today().year)
                        annual[key]["won"] += pr.amount
                        mkey = f"{draw.year}-{draw.month:02d}" if draw else None
                        if mkey:
                            monthly[(mkey, "won")] += pr.amount
            except Exception:
                continue

        report = GrowthReport()
        report.total_days = len(set(buy_dates))
        report.current_streak, report.max_streak = cls._streaks(buy_dates)
        report.consecutive_wins = cls._consecutive_wins(win_dates, date.today())

        # 月度汇总
        for (mkey, kind), val in monthly.items():
            report.monthly_summary.setdefault(mkey, {"spent": 0.0, "won": 0.0})
            report.monthly_summary[mkey][kind] = round(val, 2)

        # 年度汇总
        for y, d in annual.items():
            spent = d["spent"]
            d["roi"] = round((d["won"] - spent) / spent, 4) if spent else 0.0
            d["spent"] = round(d["spent"], 2)
            d["won"] = round(d["won"], 2)
        report.annual_summary = annual

        return report


def growth_report(tickets: List[dict], lottery: str = "dlt") -> GrowthReport:
    """便捷函数：个人成长报告。"""
    return PersonalGrowthEngine.build(tickets, lottery)
