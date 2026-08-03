"""growth_system - 用户成长系统（v4.3 P4）。

不是游戏化，而是「Atlas 使用成长」：
  保存票据次数 / 完成兑奖次数 / 查看报告次数 / 连续使用周数 → 年度 Atlas Report

数据来自 user_events（真实用户行为事件，非猜测）。
红线：成长 = 使用深度，不代表中奖能力，不诱导购彩。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

DISCLAIMER = "成长数据反映你在 Atlas 的使用情况，不代表中奖能力。彩票开奖结果具有随机性。"

LEVELS = (
    ("见习", 1, 1),     # 连续 1 周
    ("进阶", 3, 5),     # 连续 3 周且 ≥5 张票据
    ("活跃", 8, 10),    # 连续 8 周
    ("资深", 16, 20),   # 连续 16 周
    ("长期用户", 26, 30),  # 连续 26 周
)


@dataclass
class AnnualGrowth:
    """年度 Atlas Report（一年使用成长）。"""

    year: int
    tickets_saved: int = 0
    claims_completed: int = 0
    reports_viewed: int = 0
    active_weeks: int = 0
    top_activity: str = ""

    def to_dict(self) -> dict:
        return {"year": self.year, "tickets_saved": self.tickets_saved,
                "claims_completed": self.claims_completed,
                "reports_viewed": self.reports_viewed,
                "active_weeks": self.active_weeks,
                "top_activity": self.top_activity}


@dataclass
class GrowthReport:
    """用户成长报告。"""

    tickets_saved: int = 0
    claims_completed: int = 0
    reports_viewed: int = 0
    active_weeks: int = 0
    streak_weeks: int = 0
    total_events: int = 0
    level: str = "见习"
    annual: List[AnnualGrowth] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {"tickets_saved": self.tickets_saved,
                "claims_completed": self.claims_completed,
                "reports_viewed": self.reports_viewed,
                "active_weeks": self.active_weeks,
                "streak_weeks": self.streak_weeks,
                "total_events": self.total_events,
                "level": self.level,
                "annual": [a.to_dict() for a in self.annual],
                "disclaimer": self.disclaimer}

    def summary_text(self) -> str:
        lines = ["🌱 我的 Atlas 成长"]
        lines.append(f"· 保存票据：{self.tickets_saved} 次")
        lines.append(f"· 完成兑奖：{self.claims_completed} 次")
        lines.append(f"· 查看报告：{self.reports_viewed} 次")
        lines.append(f"· 连续使用：{self.streak_weeks} 周（累计 {self.active_weeks} 周）")
        lines.append(f"· 成长等级：{self.level}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class GrowthEngine:
    """用户成长引擎（基于真实事件）。"""

    @classmethod
    def _events_of(cls, events: List, year: int) -> List:
        ys = str(year)
        return [e for e in events if (e.created_at or "")[:4] == ys]

    @staticmethod
    def _iso_week(dt_str: str) -> Optional[tuple]:
        try:
            d = datetime.fromisoformat(dt_str).date()
            iso = d.isocalendar()
            return iso[0], iso[1]
        except (ValueError, TypeError):
            return None

    @classmethod
    def active_weeks(cls, events: List) -> int:
        """使用过的周数（基于 app_opened）。"""
        weeks = {cls._iso_week(e.created_at) for e in events
                 if e.event_type == "app_opened"}
        weeks.discard(None)
        return len(weeks)

    @classmethod
    def streak_weeks(cls, events: List) -> int:
        """连续使用周数：从最近活跃周向前连续。"""
        weeks = {cls._iso_week(e.created_at) for e in events
                 if e.event_type == "app_opened"}
        weeks.discard(None)
        if not weeks:
            return 0
        # 转绝对周序号（以周一日期计算），跨年安全
        seq = set()
        for y, w in weeks:
            try:
                monday = date.fromisocalendar(y, w, 1)
                seq.add((monday - date(2020, 1, 1)).days // 7)
            except ValueError:
                continue
        if not seq:
            return 0
        ordered = sorted(seq)
        # 从最近周向前连续
        streak = 1
        for i in range(len(ordered) - 1, 0, -1):
            if ordered[i] - ordered[i - 1] == 1:
                streak += 1
            else:
                break
        return streak

    @classmethod
    def level_of(cls, streak_weeks: int, tickets_saved: int) -> str:
        """成长等级（连续周数为主，票据数为辅）。"""
        level = "见习"
        for name, weeks, tickets in LEVELS:
            if streak_weeks >= weeks or tickets_saved >= tickets:
                level = name
        return level

    @classmethod
    def build(cls, events: Optional[List] = None) -> GrowthReport:
        """构建成长报告（缺省读取 EventTracker）。"""
        if events is None:
            from engine.user_events import EventTracker
            events = EventTracker().all()
        rep = GrowthReport()
        rep.total_events = len(events)
        rep.tickets_saved = sum(1 for e in events if e.event_type == "ticket_saved")
        rep.claims_completed = sum(1 for e in events if e.event_type == "claim_confirmed")
        rep.reports_viewed = sum(1 for e in events if e.event_type == "report_generated")
        rep.active_weeks = cls.active_weeks(events)
        rep.streak_weeks = cls.streak_weeks(events)
        rep.level = cls.level_of(rep.streak_weeks, rep.tickets_saved)
        # 年度
        years = sorted({(e.created_at or "")[:4] for e in events
                        if e.created_at and (e.created_at or "")[:4].isdigit()})
        for y in years:
            rep.annual.append(cls.annual_report(events, int(y)))
        return rep

    @classmethod
    def annual_report(cls, events: List, year: int) -> AnnualGrowth:
        """年度 Atlas Report。"""
        ys = str(year)
        year_evs = [e for e in events if (e.created_at or "")[:4] == ys]
        a = AnnualGrowth(year=year)
        if not year_evs:
            return a
        a.tickets_saved = sum(1 for e in year_evs if e.event_type == "ticket_saved")
        a.claims_completed = sum(1 for e in year_evs if e.event_type == "claim_confirmed")
        a.reports_viewed = sum(1 for e in year_evs if e.event_type == "report_generated")
        a.active_weeks = cls.active_weeks(year_evs)
        # 主要活动
        counts = {
            "保存票据": a.tickets_saved, "完成兑奖": a.claims_completed,
            "查看报告": a.reports_viewed,
        }
        if any(counts.values()):
            a.top_activity = max(counts, key=counts.get)
        return a


def build_growth(events: Optional[List] = None) -> GrowthReport:
    """便捷函数。"""
    return GrowthEngine.build(events)
