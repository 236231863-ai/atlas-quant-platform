"""user_simulation - 用户留存模拟（v4.2 Phase 6 用户测试）。

模拟 50 个用户的行为轨迹，观察：
  第一次打开 / 第一次保存 / 第一次开奖提醒 / 第一次兑奖 / 30天使用

行为概率模型（确定性，seed 固定可复现）：
  - 打开概率随天数衰减（留存曲线）
  - 首次保存：打开后 50% 概率
  - 提醒：保存后 80% 概率
  - 兑奖：提醒后 60% 概率
  - 复盘：兑奖后 50% 概率
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_USERS = 50
SIM_DAYS = 30


@dataclass
class SimulatedUser:
    """一个模拟用户的行为轨迹。"""

    user_id: int
    first_opened_day: int = 0
    first_saved_day: int = -1        # -1 = 未保存
    first_reminded_day: int = -1
    first_claimed_day: int = -1
    first_reviewed_day: int = -1
    open_days: List[int] = field(default_factory=list)
    saved_count: int = 0
    claimed_count: int = 0

    @property
    def saved(self) -> bool:
        return self.first_saved_day >= 0

    @property
    def reminded(self) -> bool:
        return self.first_reminded_day >= 0

    @property
    def claimed(self) -> bool:
        return self.first_claimed_day >= 0

    @property
    def reviewed(self) -> bool:
        return self.first_reviewed_day >= 0

    @property
    def opened_at_d7(self) -> bool:
        return 7 in self.open_days

    @property
    def opened_at_d30(self) -> bool:
        return 30 in self.open_days

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "first_opened_day": self.first_opened_day,
            "first_saved_day": self.first_saved_day,
            "first_reminded_day": self.first_reminded_day,
            "first_claimed_day": self.first_claimed_day,
            "first_reviewed_day": self.first_reviewed_day,
            "open_days": list(self.open_days),
            "saved_count": self.saved_count,
            "claimed_count": self.claimed_count,
            "saved": self.saved,
            "reminded": self.reminded,
            "claimed": self.claimed,
            "reviewed": self.reviewed,
        }


class UserSimulation:
    """用户留存模拟器。"""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def _open_prob(self, day: int) -> float:
        """打开概率：注册日 1.0，之后衰减，下限 0.12。"""
        if day == 0:
            return 1.0
        if day == 1:
            return 0.62
        return max(0.12, 0.62 * (0.9 ** (day - 1)))

    def simulate_user(self, user_id: int) -> SimulatedUser:
        """模拟一个用户 30 天行为。"""
        u = SimulatedUser(user_id=user_id)
        saved = False
        for day in range(SIM_DAYS + 1):
            # 打开
            if self._rng.random() < self._open_prob(day):
                u.open_days.append(day)
                if u.first_opened_day == 0 and day == 0:
                    u.first_opened_day = 0
                elif not u.open_days and day == 0:
                    u.first_opened_day = 0
                # 首次保存（每次打开 15% 概率，30 天累计约 60~70%）
                if not saved and day >= 1 and self._rng.random() < 0.15:
                    u.first_saved_day = day
                    saved = True
                    u.saved_count = 1
                # 已保存 → 继续购彩（低概率）
                elif saved and self._rng.random() < 0.25:
                    u.saved_count += 1
            # 提醒（保存后一次性判定 80%）
            if saved and u.first_reminded_day < 0 and day == u.first_saved_day + 1:
                if self._rng.random() < 0.8:
                    u.first_reminded_day = day
            # 兑奖（提醒后一次性判定 60%）
            if u.first_reminded_day >= 0 and u.first_claimed_day < 0 and day == u.first_reminded_day + 1:
                if self._rng.random() < 0.6:
                    u.first_claimed_day = day
                    u.claimed_count += 1
            # 复盘（兑奖后一次性判定 50%）
            if u.first_claimed_day >= 0 and u.first_reviewed_day < 0 and day == u.first_claimed_day + 1:
                if self._rng.random() < 0.5:
                    u.first_reviewed_day = day
        # 兜底：day0 一定打开（注册即打开）
        if not u.open_days:
            u.open_days = [0]
        return u

    @classmethod
    def generate(cls, n: int = DEFAULT_USERS, seed: int = 42) -> List[SimulatedUser]:
        """生成 n 个模拟用户。"""
        sim = cls(seed)
        return [sim.simulate_user(i) for i in range(n)]

    @classmethod
    def cohort_stats(cls, users: List[SimulatedUser]) -> dict:
        """留存漏斗统计。"""
        n = len(users)
        if n == 0:
            return {"total": 0}

        def rate(cond) -> float:
            return sum(1 for u in users if cond(u)) / n

        opened = rate(lambda u: u.first_opened_day == 0)
        saved = rate(lambda u: u.saved)
        reminded = rate(lambda u: u.reminded)
        claimed = rate(lambda u: u.claimed)
        reviewed = rate(lambda u: u.reviewed)
        d7 = rate(lambda u: u.opened_at_d7)
        d30 = rate(lambda u: u.opened_at_d30)

        return {
            "total": n,
            "first_open": round(opened, 4),
            "save_rate": round(saved, 4),
            "remind_rate": round(reminded, 4),
            "claim_rate": round(claimed, 4),
            "review_rate": round(reviewed, 4),
            "retention_d7": round(d7, 4),
            "retention_d30": round(d30, 4),
            "funnel": {
                "opened": round(opened, 4),
                "saved": round(saved, 4),
                "reminded": round(reminded, 4),
                "claimed": round(claimed, 4),
                "reviewed": round(reviewed, 4),
            },
        }

    @classmethod
    def funnel_text(cls, stats: dict) -> str:
        """漏斗文本（User_Retention_Test.md 用）。"""
        f = stats.get("funnel", {})
        lines = [f"· 总用户：{stats.get('total', 0)}"]
        lines.append(f"· 第一次打开：{f.get('opened', 0) * 100:.0f}%")
        lines.append(f"· 第一次保存：{f.get('saved', 0) * 100:.0f}%")
        lines.append(f"· 第一次提醒：{f.get('reminded', 0) * 100:.0f}%")
        lines.append(f"· 第一次兑奖：{f.get('claimed', 0) * 100:.0f}%")
        lines.append(f"· 复盘查看：{f.get('reviewed', 0) * 100:.0f}%")
        lines.append(f"· D7 留存：{stats.get('retention_d7', 0) * 100:.0f}%")
        lines.append(f"· D30 留存：{stats.get('retention_d30', 0) * 100:.0f}%")
        return "\n".join(lines)
