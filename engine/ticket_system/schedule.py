"""ticket_system - 彩票开奖日程（LotterySchedule）。

彩种开奖日：
  - 大乐透：周一 / 三 / 六
  - 双色球：周二 / 四 / 日

用途：给定购买日期，推算购买后的最近一次开奖日。
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

# 彩种 → 开奖日（weekday: 周一=0 ... 周日=6）
LOTTERY_SCHEDULE = {
    "dlt": {0, 2, 5},   # 周一、三、六
    "ssq": {1, 3, 6},   # 周二、四、日
}


def _to_date(d: str) -> Optional[date]:
    try:
        if len(d) == 5:  # MM-DD
            return datetime.strptime(f"{date.today().year}-{d}", "%Y-%m-%d").date()
        return datetime.strptime(d, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class LotterySchedule:
    """开奖日程计算器。"""

    @staticmethod
    def next_draw_date(lottery: str, from_date: str) -> Optional[str]:
        """给定日期（含当天）之后最近的符合开奖日的日期。"""
        dows = LOTTERY_SCHEDULE.get(lottery, LOTTERY_SCHEDULE["dlt"])
        d = _to_date(from_date)
        if d is None:
            return None
        for _ in range(8):
            if d.weekday() in dows:
                return d.isoformat()
            d += timedelta(days=1)
        return None

    @staticmethod
    def is_draw_day(lottery: str, date_str: str) -> bool:
        d = _to_date(date_str)
        if d is None:
            return False
        return d.weekday() in LOTTERY_SCHEDULE.get(lottery, LOTTERY_SCHEDULE["dlt"])

    @staticmethod
    def lottery_name(lottery: str) -> str:
        return "大乐透" if lottery == "dlt" else "双色球"
