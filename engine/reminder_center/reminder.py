"""reminder_center - 开奖提醒引擎（v4.1 阶段2）。

TodayReminder：今天为什么打开 Atlas。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

DISCLAIMER = "提醒仅为开奖日程与票据管理，不涉及预测。彩票开奖结果具有随机性。"


@dataclass
class TodayReminder:
    """今日提醒报告。"""

    today: str = ""
    draw_today: List[str] = field(default_factory=list)      # 今日开奖彩种
    prize_due: int = 0                                       # 今日可兑奖票据数
    unclaimed: int = 0                                       # 未兑奖票据数
    chase_notes: List[dict] = field(default_factory=list)    # 追号提醒
    next_draws: List[dict] = field(default_factory=list)     # 未来开奖
    disclaimer: str = DISCLAIMER

    @property
    def has_anything(self) -> bool:
        return bool(self.draw_today) or self.prize_due > 0 or self.unclaimed > 0 or bool(self.chase_notes)

    def to_dict(self) -> dict:
        return {
            "today": self.today, "draw_today": self.draw_today,
            "prize_due": self.prize_due, "unclaimed": self.unclaimed,
            "chase_notes": self.chase_notes, "next_draws": self.next_draws,
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = [f"🔔 今日提醒（{self.today}）"]
        if self.draw_today:
            lines.append("· 🎯 今日开奖：" + "、".join(self.draw_today) + "，快去查你的彩票！")
        else:
            lines.append("· 今日无开奖")
        if self.prize_due > 0:
            lines.append(f"· 💰 有 {self.prize_due} 张票据今天可兑奖")
        if self.unclaimed > 0:
            lines.append(f"· ⏳ 有 {self.unclaimed} 张票据已开奖未确认")
        for ch in self.chase_notes[:5]:
            front = " ".join(f"{n:02d}" for n in ch["front"])
            lines.append(f"· 🔁 你追的 [{front}] 已连续 {ch['streak']} 期")
        if self.next_draws:
            lines.append("· 📅 下次开奖：")
            for nd in self.next_draws[:3]:
                lines.append(f"  - {nd['lottery_name']} {nd['date']}")
        if not self.has_anything:
            lines.append("· 今天没有紧急事项，可查看个人报告或设置预算")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class ReminderEngine:
    """开奖提醒引擎。"""

    @staticmethod
    def _today() -> str:
        return date.today().isoformat()

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
    def _draw_today(cls) -> List[str]:
        """今日开奖彩种。"""
        from engine.ticket_system.schedule import LotterySchedule
        today = cls._today()
        out = []
        for lot, name in (("dlt", "大乐透"), ("ssq", "双色球")):
            if LotterySchedule.is_draw_day(lot, today):
                out.append(name)
        return out

    @classmethod
    def _next_draws(cls) -> List[dict]:
        """未来 5 天开奖。"""
        from engine.ticket_system.schedule import LotterySchedule
        today = date.today()
        out = []
        for offset in range(1, 8):
            d = (today + timedelta(days=offset)).isoformat()
            for lot, name in (("dlt", "大乐透"), ("ssq", "双色球")):
                if LotterySchedule.is_draw_day(lot, d):
                    out.append({"lottery": lot, "lottery_name": name, "date": d})
        return out

    @classmethod
    def _ticket_reminders(cls, tickets: List[dict]) -> tuple:
        """返回 (今日可兑奖数, 未兑奖数)。"""
        today = cls._today()
        prize_due = 0
        unclaimed = 0
        for t in tickets:
            draw = cls._parse_date(t.get("draw_date") or "")
            if draw:
                if draw.isoformat() == today:
                    prize_due += 1
                elif draw.isoformat() < today:
                    unclaimed += 1
            else:
                buy = cls._parse_date(t.get("buy_date") or "")
                if buy and buy.isoformat() <= today:
                    unclaimed += 1
        return prize_due, unclaimed

    @classmethod
    def _chase_reminders(cls, tickets: List[dict]) -> List[dict]:
        """追号提醒：相同组合出现 ≥2 次，统计连续期数。"""
        combo_dates = {}
        for t in tickets:
            key = (tuple(t.get("front", [])), tuple(t.get("back", [])))
            d = t.get("buy_date") or t.get("saved_at", "")[:10]
            combo_dates.setdefault(key, []).append(d)
        out = []
        for (front, back), ds in combo_dates.items():
            valid = sorted(d for d in ds if d)
            if len(set(valid)) >= 2:
                out.append({
                    "front": list(front), "back": list(back),
                    "streak": len(set(valid)),
                })
        return out

    @classmethod
    def build(cls, tickets: List[dict], today: Optional[str] = None) -> TodayReminder:
        """构建今日提醒。"""
        t = today or cls._today()
        prize_due, unclaimed = cls._ticket_reminders(tickets)
        return TodayReminder(
            today=t,
            draw_today=cls._draw_today(),
            prize_due=prize_due,
            unclaimed=unclaimed,
            chase_notes=cls._chase_reminders(tickets),
            next_draws=cls._next_draws(),
        )


def today_reminders(tickets: List[dict]) -> TodayReminder:
    """便捷函数：今日提醒。"""
    return ReminderEngine.build(tickets)
