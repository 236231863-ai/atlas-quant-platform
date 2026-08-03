"""live_draw.health - Data Health Center（v4.4 P3）。

数据可信中心：
  - 最新期号 / 开奖日期 / 更新时间 / 数据来源 / 数据状态
  - 等级：A 正常同步 / B 超12h / C 超24h / D 数据异常
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}
LEVELS = ("A", "B", "C", "D")


@dataclass
class DataHealth:
    """一个彩种的数据健康报告。"""

    lottery: str = "dlt"
    latest_issue: str = ""
    draw_date: str = ""
    updated_at: str = ""
    source: str = ""
    total: int = 0
    age_hours: float = -1.0
    level: str = "D"
    message: str = ""

    @property
    def lottery_name(self) -> str:
        return LOTTERY_NAMES.get(self.lottery, self.lottery)

    @property
    def age_text(self) -> str:
        if self.age_hours < 0:
            return "未知"
        if self.age_hours < 1:
            return f"{int(self.age_hours * 60)} 分钟前"
        return f"{self.age_hours:.1f} 小时前"

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "lottery_name": self.lottery_name,
                "latest_issue": self.latest_issue, "draw_date": self.draw_date,
                "updated_at": self.updated_at, "source": self.source,
                "total": self.total, "age_hours": round(self.age_hours, 1),
                "age_text": self.age_text, "level": self.level,
                "message": self.message}

    def summary_text(self) -> str:
        return (f"🩺 {self.lottery_name}数据可信：{self.level} 级\n"
                f"· 最新期号：{self.latest_issue or '无'}（{self.draw_date or '无日期'}）\n"
                f"· 更新时间：{self.age_text}\n"
                f"· 数据来源：{self.source or '未知'}\n"
                f"· {self.message}")


class DataHealthCenter:
    """数据可信中心。"""

    LEVEL_MESSAGES = {
        "A": "正常同步",
        "B": "超过 12 小时未更新",
        "C": "超过 24 小时未更新",
        "D": "数据异常",
    }

    @classmethod
    def _age_hours(cls, updated_at: Optional[str],
                   now: Optional[datetime] = None) -> float:
        """计算数据年龄（小时）。updated_at 为空返回 -1。"""
        if not updated_at:
            return -1.0
        now = now or datetime.now()
        try:
            dt = datetime.fromisoformat(updated_at)
            return max(0.0, (now - dt).total_seconds() / 3600)
        except ValueError:
            return -1.0

    @classmethod
    def level_of(cls, age_hours: float, has_data: bool = True) -> str:
        """等级判定：A <12h / B 12-24h / C >24h / D 异常。"""
        if not has_data:
            return "D"
        if age_hours < 0:
            return "D"
        if age_hours < 12:
            return "A"
        if age_hours < 24:
            return "B"
        return "C"

    @classmethod
    def check(cls, lottery: str = "dlt",
              now: Optional[datetime] = None) -> DataHealth:
        """检查一个彩种的数据健康。"""
        from engine.data_center_v2.updater import IncrementalUpdater

        now = now or datetime.now()
        up = IncrementalUpdater(lottery)
        rows = up.load_local()
        if not rows:
            rows = up._load_builtin()
        has_data = bool(rows)
        if not has_data:
            return DataHealth(lottery=lottery, level="D",
                              message=cls.LEVEL_MESSAGES["D"])

        latest = rows[-1]
        updated_at = up._last_update()
        age = cls._age_hours(updated_at, now)
        level = cls.level_of(age, has_data)

        # 来源
        source = "用户缓存"
        if os_path_in_atlas_raw(up.cache_path()):
            source = "实时更新（官方 API）"

        return DataHealth(
            lottery=lottery,
            latest_issue=latest["issue"],
            draw_date=latest["date"],
            updated_at=updated_at or "",
            source=source,
            total=len(rows),
            age_hours=age,
            level=level,
            message=cls.LEVEL_MESSAGES[level],
        )

    @classmethod
    def check_all(cls, now: Optional[datetime] = None) -> list:
        """检查所有彩种。"""
        out = []
        for lot in ("dlt", "ssq"):
            out.append(cls.check(lot, now=now))
        return out


def os_path_in_atlas_raw(path: str) -> bool:
    """路径是否位于 ~/.atlas/raw（实时更新缓存）。"""
    import os
    return ".atlas" in os.path.normpath(path).split(os.sep) and "raw" in os.path.normpath(path).split(os.sep)


def check_data_health(lottery: str = "dlt") -> DataHealth:
    """便捷函数。"""
    return DataHealthCenter.check(lottery)
