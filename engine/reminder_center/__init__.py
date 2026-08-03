"""reminder_center - 开奖提醒中心（v4.1 阶段2）。

回答「今天为什么打开 Atlas」：
  - 开奖提醒：今天哪些彩种开奖
  - 兑奖提醒：今天可兑奖的票据
  - 未兑奖提醒：已开奖但未确认的票据
  - 遗漏提醒：追号组合的连续期数

复用 LotterySchedule 开奖日程。
"""
from .reminder import ReminderEngine, TodayReminder, DrawCountdown, today_reminders

__all__ = ["ReminderEngine", "TodayReminder", "DrawCountdown", "today_reminders"]
