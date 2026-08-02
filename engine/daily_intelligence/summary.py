"""daily_intelligence - 每日智能摘要（DailySummary）。

对比「上次快照」与「当前数据」，输出用户关心的每日变化：
  - 数据变化   : 新增期数、最新号码、时间范围
  - 号码统计变化 : 热号 TOP 变化、号码频率增减
  - 趋势变化   : 和值趋势、奇偶比变化、跨度变化
  - 报告提醒   : 是否有值得生成报告的信号（如数据更新、格局变化）

⚠️ 严格禁止任何中奖预测 —— 所有输出为「变化观察」与「统计事实」。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DailySummary:
    """每日智能摘要。"""

    date: str = ""
    new_draws: int = 0
    latest_issue: str = ""
    latest_date: str = ""
    latest_numbers: str = ""
    date_range: str = ""
    hot_top_before: List[int] = field(default_factory=list)
    hot_top_after: List[int] = field(default_factory=list)
    hot_changed: bool = False
    rising_numbers: List[Tuple[int, int]] = field(default_factory=list)   # (号, 增幅)
    falling_numbers: List[Tuple[int, int]] = field(default_factory=list)  # (号, 降幅)
    avg_sum_before: float = 0.0
    avg_sum_after: float = 0.0
    sum_trend: str = "stable"  # up / down / stable
    odd_even_before: Optional[str] = None
    odd_even_after: Optional[str] = None
    reminder: List[str] = field(default_factory=list)

    def to_text(self) -> str:
        """渲染为可读文本（UI/通知用）。"""
        lines = [f"📅 Atlas 每日摘要 · {self.date}"]
        if self.new_draws > 0:
            lines.append(f"· 新增 {self.new_draws} 期数据，最新 {self.latest_issue}（{self.latest_date}）")
            lines.append(f"· 最新号码：{self.latest_numbers}")
        else:
            lines.append("· 今日无新增数据")
        lines.append(f"· 热号 TOP：{' '.join(f'{n:02d}' for n in self.hot_top_after)}"
                     + ("（较上次有变化）" if self.hot_changed else ""))
        if self.rising_numbers:
            lines.append("· 上升号：" + " ".join(f"{n:02d}(+{c})" for n, c in self.rising_numbers[:5]))
        if self.falling_numbers:
            lines.append("· 下降号：" + " ".join(f"{n:02d}({c})" for n, c in self.falling_numbers[:5]))
        lines.append(f"· 平均和值 {self.avg_sum_after:.1f}（趋势{'↑' if self.sum_trend=='up' else '↓' if self.sum_trend=='down' else '→'}）")
        if self.odd_even_after:
            lines.append(f"· 奇偶比 {self.odd_even_after}")
        for r in self.reminder:
            lines.append(f"· 💡 {r}")
        lines.append("· 本摘要为统计观察，非中奖预测。彩票开奖独立随机。")
        return "\n".join(lines)

    def has_reminder(self) -> bool:
        return len(self.reminder) > 0

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "new_draws": self.new_draws,
            "latest_issue": self.latest_issue,
            "latest_date": self.latest_date,
            "latest_numbers": self.latest_numbers,
            "date_range": self.date_range,
            "hot_changed": self.hot_changed,
            "rising_numbers": self.rising_numbers,
            "falling_numbers": self.falling_numbers,
            "avg_sum_after": round(self.avg_sum_after, 1),
            "sum_trend": self.sum_trend,
            "odd_even_after": self.odd_even_after,
            "reminder": self.reminder,
        }


def _frequency(draws) -> Dict[int, int]:
    c: Counter = Counter()
    for d in draws:
        c.update(d.front)
    return dict(c)


def _avg_sum(draws) -> float:
    if not draws:
        return 0.0
    return sum(d.front_sum for d in draws) / len(draws)


def _odd_even(draws) -> Optional[str]:
    if not draws:
        return None
    odd = sum(1 for d in draws for n in d.front if n % 2 == 1)
    even = sum(1 for d in draws for n in d.front if n % 2 == 0)
    return f"{odd}:{even}"


def build_summary(previous: list, current: list, date: str = "") -> DailySummary:
    """构建每日摘要。

    Args:
        previous: 上次快照的数据（可能为空 = 首次）。
        current: 当前数据（需为按时间升序）。
        date: 摘要日期。
    """
    s = DailySummary(date=date or "今日")
    if not current:
        return s

    # 数据变化
    prev_ids = {d.number for d in previous} if previous else set()
    cur_ids = {d.number for d in current}
    s.new_draws = len(cur_ids - prev_ids)
    last = current[-1]
    s.latest_issue = last.number
    s.latest_date = last.draw_date
    s.latest_numbers = f"{last.format_front()} + {last.format_back()}"
    s.date_range = f"{current[0].draw_date} ~ {last.draw_date}"

    # 号码统计变化
    f_before = _frequency(previous)
    f_after = _frequency(current)
    hot_before = sorted(f_before, key=lambda n: (f_before[n], n), reverse=True)[:8] if f_before else []
    hot_after = sorted(f_after, key=lambda n: (f_after[n], n), reverse=True)[:8] if f_after else []
    s.hot_top_before = hot_before
    s.hot_top_after = hot_after
    s.hot_changed = set(hot_before) != set(hot_after)

    all_nums = set(range(1, 36))
    if f_before:
        rising = [(n, f_after.get(n, 0) - f_before.get(n, 0)) for n in all_nums
                  if f_after.get(n, 0) > f_before.get(n, 0)]
        falling = [(n, f_before.get(n, 0) - f_after.get(n, 0)) for n in all_nums
                   if f_after.get(n, 0) < f_before.get(n, 0)]
        s.rising_numbers = sorted(rising, key=lambda x: -x[1])[:8]
        s.falling_numbers = sorted(falling, key=lambda x: -x[1])[:8]

    # 趋势变化
    avg_before = _avg_sum(previous)
    avg_after = _avg_sum(current)
    s.avg_sum_before = avg_before
    s.avg_sum_after = avg_after
    if avg_before > 0:
        if avg_after > avg_before * 1.02:
            s.sum_trend = "up"
        elif avg_after < avg_before * 0.98:
            s.sum_trend = "down"
        else:
            s.sum_trend = "stable"
    s.odd_even_before = _odd_even(previous)
    s.odd_even_after = _odd_even(current)

    # 报告提醒（仅观察信号，非预测）
    if s.new_draws > 0:
        s.reminder.append(f"新增 {s.new_draws} 期数据，可生成最新报告")
    if s.hot_changed and f_before:
        s.reminder.append("热号格局发生变化，值得关注")
    if len(current) >= 500:
        s.reminder.append("数据充足（≥500 期），统计结论更稳健")
    if len(s.reminder) >= 3:
        s.reminder = s.reminder[:3]
    return s
