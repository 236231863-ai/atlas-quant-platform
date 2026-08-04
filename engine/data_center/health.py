"""data_center.health - DataHealthReport（v4.5 P1）。

输出各彩种数据状态：最新期 / 日期 / 来源 / 状态。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class LotteryHealth:
    """单彩种数据健康。"""

    lottery: str
    latest_issue: str = ""
    draw_date: str = ""
    source: str = ""
    status: str = "未知"      # 可信 / 过期 / 异常
    updated_at: str = ""
    age_hours: float = -1.0
    valid: bool = True
    total: int = 0

    @property
    def lottery_name(self) -> str:
        return LOTTERY_NAMES.get(self.lottery, self.lottery)

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "lottery_name": self.lottery_name,
                "latest_issue": self.latest_issue, "draw_date": self.draw_date,
                "source": self.source, "status": self.status,
                "updated_at": self.updated_at, "age_hours": round(self.age_hours, 1),
                "valid": self.valid, "total": self.total}

    def summary_text(self) -> str:
        return (f"{self.lottery_name}：最新期 {self.latest_issue or '无'} · "
                f"{self.draw_date or '无日期'} · 来源 {self.source or '未知'} · "
                f"状态 {self.status}")


@dataclass
class DataHealthReport:
    """全部彩种数据健康报告。"""

    items: List[LotteryHealth] = field(default_factory=list)

    @property
    def all_trusted(self) -> bool:
        return bool(self.items) and all(i.status == "可信" for i in self.items)

    def to_dict(self) -> dict:
        return {"items": [i.to_dict() for i in self.items],
                "all_trusted": self.all_trusted}

    def summary_text(self) -> str:
        lines = ["🩺 开奖数据健康报告"]
        for it in self.items:
            lines.append("· " + it.summary_text())
        return "\n".join(lines)


class DataHealthBuilder:
    """构建 DataHealthReport。"""

    @classmethod
    def build(cls, now: Optional[datetime] = None) -> DataHealthReport:
        """检查所有彩种的数据健康。"""
        now = now or datetime.now()
        items = []
        for lottery in ("dlt", "ssq"):
            items.append(cls._check_lottery(lottery, now))
        return DataHealthReport(items=items)

    @classmethod
    def _check_lottery(cls, lottery: str, now: datetime) -> LotteryHealth:
        """检查单彩种。"""
        from engine.data_center.providers import LocalCache
        from engine.data_center_v2.updater import IncrementalUpdater

        # 本地缓存数据
        cache = LocalCache(lottery)
        records = cache.fetch_recent(limit=1)
        up = IncrementalUpdater(lottery)
        updated_at = up._last_update()
        age = cls._age(updated_at, now)

        if not records:
            return LotteryHealth(lottery=lottery, status="异常", valid=False)

        latest = records[-1]
        # 状态判定
        if age < 0:
            status = "异常"
        elif age < 12:
            status = "可信"
        elif age < 24:
            status = "过期"
        else:
            status = "过期"

        return LotteryHealth(
            lottery=lottery,
            latest_issue=latest.number,
            draw_date=latest.draw_date,
            source="官方API" if cls._is_official(lottery) else "本地缓存",
            status=status,
            updated_at=updated_at or "",
            age_hours=age,
            valid=True,
            total=cls._total(lottery),
        )

    @staticmethod
    def _is_official(lottery: str) -> bool:
        # 缓存由官方 API 更新器写入（~/.atlas/raw）即为官方来源
        import os
        p = os.path.join(os.path.expanduser("~"), ".atlas", "raw", f"{lottery}_history.csv")
        return os.path.exists(p)

    @staticmethod
    def _total(lottery: str) -> int:
        from engine.data_center.providers import LocalCache
        return len(LocalCache(lottery).fetch_recent(limit=100000))

    @staticmethod
    def _age(updated_at: Optional[str], now: datetime) -> float:
        if not updated_at:
            return -1.0
        try:
            dt = datetime.fromisoformat(updated_at)
            return max(0.0, (now - dt).total_seconds() / 3600)
        except ValueError:
            return -1.0


def build_health_report(now: Optional[datetime] = None) -> DataHealthReport:
    """便捷函数。"""
    return DataHealthBuilder.build(now)
