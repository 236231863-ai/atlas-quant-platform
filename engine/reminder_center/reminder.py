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
class DrawCountdown:
    """下一开奖倒计时（v4.3 P1）。"""

    lottery: str = ""
    lottery_name: str = ""
    next_draw_date: str = ""
    days: int = 0
    hours: int = 0

    @property
    def is_soon(self) -> bool:
        """未来 48 小时内开奖。"""
        return self.days <= 2

    def text(self) -> str:
        if not self.next_draw_date:
            return "暂无开奖日程"
        if self.days <= 0 and self.hours <= 0:
            return f"📅 {self.lottery_name} 今日开奖"
        if self.days <= 0:
            return f"📅 {self.lottery_name} 今日开奖（约 {self.hours} 小时后）"
        return f"📅 {self.lottery_name} 距开奖 {self.days} 天（{self.next_draw_date}）"

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "lottery_name": self.lottery_name,
                "next_draw_date": self.next_draw_date, "days": self.days,
                "hours": self.hours}


@dataclass
class TodayReminder:
    """今日提醒报告（v4.1.1：票据状态机 + 通知文本）。"""

    today: str = ""
    draw_today: List[str] = field(default_factory=list)      # 今日开奖彩种
    prize_due: int = 0                                       # 今日可兑奖票据数
    unclaimed: int = 0                                       # 未兑奖票据数
    chase_notes: List[dict] = field(default_factory=list)    # 追号提醒
    next_draws: List[dict] = field(default_factory=list)     # 未来开奖
    ticket_status: dict = field(default_factory=dict)        # 状态机计数
    countdown: Optional[DrawCountdown] = None                # v4.3 P1 下一开奖倒计时
    disclaimer: str = DISCLAIMER

    def notify_text(self) -> str:
        """桌面通知文案（v4.1.1 Phase 1）。"""
        if self.draw_today:
            names = "、".join(self.draw_today)
            if self.prize_due > 0:
                return f"🎯 今晚{names}开奖，你有 {self.prize_due} 张彩票等待兑奖"
            return f"🎯 今晚{names}开奖，去查你的彩票！"
        if self.prize_due > 0:
            return f"💰 你有 {self.prize_due} 张彩票今天可兑奖"
        if self.unclaimed > 0:
            return f"⏳ 你有 {self.unclaimed} 张已开奖彩票未确认"
        return "📋 打开 Atlas，看看你的彩票状态"

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
        if self.countdown and self.countdown.next_draw_date:
            lines.append(f"· {self.countdown.text()}")
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
    def next_countdown(cls, lottery: str = "dlt") -> DrawCountdown:
        """下一开奖倒计时（v4.3 P1）。"""
        from engine.ticket_system.schedule import LotterySchedule
        name = "大乐透" if lottery == "dlt" else ("双色球" if lottery == "ssq" else lottery)
        today = date.today()
        for offset in range(0, 8):
            d = today + timedelta(days=offset)
            if LotterySchedule.is_draw_day(lottery, d.isoformat()):
                days = offset
                hours = 24 - datetime.now().hour if offset == 0 else offset * 24
                return DrawCountdown(lottery=lottery, lottery_name=name,
                                     next_draw_date=d.isoformat(),
                                     days=days, hours=hours)
        return DrawCountdown(lottery=lottery, lottery_name=name)

    @classmethod
    def notify_and_record(cls, notifier, title: str, message: str) -> bool:
        """桌面通知 + 记录用户提醒事件（v4.3 验收：用户行为发生）。"""
        ok = bool(notifier and getattr(notifier, "notify", None))
        shown = notifier.notify(title, message) if ok else False
        try:
            from engine.user_events import EventTracker
            EventTracker().record("reminder_shown", {
                "title": title, "message": message, "shown": shown,
            })
        except Exception:
            pass
        return shown

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
    def ticket_status(cls, tickets: List[dict], today: Optional[str] = None) -> dict:
        """票据状态机（v4.1.1 Phase 1）：待开奖/已开奖待兑奖/已兑奖。"""
        t = today or cls._today()
        status = {"pending_draw": 0, "ready_claim": 0, "claimed": 0}
        for tk in tickets:
            draw = cls._parse_date(tk.get("draw_date") or "")
            if not draw:
                status["pending_draw"] += 1
                continue
            if draw.isoformat() > t:
                status["pending_draw"] += 1
            elif draw.isoformat() <= t and not tk.get("claimed"):
                status["ready_claim"] += 1
            else:
                status["claimed"] += 1
        return status

    @classmethod
    def build(cls, tickets: List[dict], today: Optional[str] = None,
              lottery: str = "dlt") -> TodayReminder:
        """构建今日提醒（v4.1.1：状态机；v4.3：开奖倒计时）。"""
        t = today or cls._today()
        prize_due, unclaimed = cls._ticket_reminders(tickets)
        return TodayReminder(
            today=t,
            draw_today=cls._draw_today(),
            prize_due=prize_due,
            unclaimed=unclaimed,
            chase_notes=cls._chase_reminders(tickets),
            next_draws=cls._next_draws(),
            ticket_status=cls.ticket_status(tickets, t),
            countdown=cls.next_countdown(lottery),
        )


def today_reminders(tickets: List[dict], lottery: str = "dlt") -> TodayReminder:
    """便捷函数：今日提醒（v4.3 支持指定彩种倒计时）。"""
    return ReminderEngine.build(tickets, lottery=lottery)
