"""data_center.providers - 数据源管理（v4.5 P1）。

DataProvider 层次：
  DataProvider（抽象）
    ├── OfficialProvider   官方 API（大乐透 gameNo=85 / 双色球 gameNo=235）
    ├── BackupProvider     备用（内置历史 CSV）
    └── LocalCache         本地缓存（~/.atlas/raw，优先读取）

每个彩种使用正确数据源：dlt → 官方85，ssq → 官方235（不可用降级内置）。
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class DrawRecord:
    """统一开奖记录。"""

    number: str
    draw_date: str = ""
    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)
    lottery: str = "dlt"
    pool: float = 0.0

    def to_dict(self) -> dict:
        return {"number": self.number, "draw_date": self.draw_date,
                "front": list(self.front), "back": list(self.back),
                "lottery": self.lottery, "pool": self.pool}


class DataProvider(ABC):
    """数据源抽象基类。"""

    name = "abstract"
    lottery = "dlt"

    @abstractmethod
    def fetch_recent(self, limit: int = 30) -> List[DrawRecord]:
        """获取最近开奖记录。"""

    def source_text(self) -> str:
        return self.name


class OfficialProvider(DataProvider):
    """官方 API 数据源（webapi.sporttery.cn）。"""

    name = "官方API"

    def __init__(self, lottery: str = "dlt"):
        self.lottery = lottery

    def fetch_recent(self, limit: int = 30) -> List[DrawRecord]:
        from engine.data_center_v2.sources import APIDatasource
        src = APIDatasource(lottery=self.lottery, pages=1, page_size=limit)
        return [DrawRecord(number=r.number, draw_date=r.draw_date,
                           front=list(r.front), back=list(r.back),
                           lottery=self.lottery, pool=r.pool)
                for r in src.load()]


class BackupProvider(DataProvider):
    """备用数据源：内置历史 CSV。"""

    name = "内置历史"

    def __init__(self, lottery: str = "dlt"):
        self.lottery = lottery

    def fetch_recent(self, limit: int = 30) -> List[DrawRecord]:
        from engine.data_center_v2.sources import CSVDatasource
        p = self._builtin_path()
        if not p or not os.path.exists(p):
            return []
        return [DrawRecord(number=r.number, draw_date=r.draw_date,
                           front=list(r.front), back=list(r.back),
                           lottery=self.lottery, pool=r.pool)
                for r in CSVDatasource(p, lottery=self.lottery).load()][-limit:]

    def _builtin_path(self) -> Optional[str]:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [os.path.join(root, "data", "raw", f"{self.lottery}_history.csv")]
        base = getattr(__import__("sys"), "_MEIPASS", None)
        if base:
            candidates.insert(0, os.path.join(base, "data", "raw", f"{self.lottery}_history.csv"))
        for p in candidates:
            if os.path.exists(p):
                return p
        return None


class LocalCache(DataProvider):
    """本地缓存数据源（~/.atlas/raw，优先读取）。"""

    name = "本地缓存"

    def __init__(self, lottery: str = "dlt", storage_dir: Optional[str] = None):
        self.lottery = lottery
        self.storage_dir = storage_dir

    def fetch_recent(self, limit: int = 30) -> List[DrawRecord]:
        from engine.data_center_v2.updater import IncrementalUpdater
        up = IncrementalUpdater(self.lottery, storage_dir=self.storage_dir)
        rows = up.load_local()
        if not rows:
            rows = up._load_builtin()
        # 按期号排序（内置 CSV 可能倒序存储），取最新 limit 条
        rows = sorted(rows, key=lambda r: int(r["issue"]))
        return [DrawRecord(number=r["issue"], draw_date=r["date"],
                           front=self._parse_front(r["numbers"]),
                           back=self._parse_back(r["numbers"]),
                           lottery=self.lottery)
                for r in rows[-limit:]]

    def _parse_front(self, numbers: str) -> List[int]:
        if "|" in numbers:
            return [int(x) for x in numbers.split("|")[0].split()]
        parts = numbers.replace(",", " ").split()
        n = 5 if self.lottery == "dlt" else 6
        return [int(x) for x in parts[:n]]

    def _parse_back(self, numbers: str) -> List[int]:
        if "|" in numbers:
            return [int(x) for x in numbers.split("|")[1].split()]
        parts = numbers.replace(",", " ").split()
        n = 5 if self.lottery == "dlt" else 6
        return [int(x) for x in parts[n:n + (2 if self.lottery == "dlt" else 1)]]


def get_provider_chain(lottery: str, storage_dir: Optional[str] = None) -> List[DataProvider]:
    """彩种数据源链（按优先级）：官方 → 备用 → 本地缓存。"""
    return [OfficialProvider(lottery), BackupProvider(lottery),
            LocalCache(lottery, storage_dir=storage_dir)]


def fetch_with_fallback(lottery: str, limit: int = 30,
                        storage_dir: Optional[str] = None) -> tuple:
    """按链拉取：官方优先，失败降级备用/本地。

    返回 (records, source_name)。
    """
    for provider in get_provider_chain(lottery, storage_dir):
        try:
            records = provider.fetch_recent(limit)
            if records:
                return records, provider.source_text()
        except Exception:
            continue
    return [], "无数据"
