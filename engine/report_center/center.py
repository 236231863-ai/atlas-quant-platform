"""report_center - 报告中心。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class PrizeReport:
    """一份兑奖报告。"""

    report_id: str
    lottery: str = "dlt"
    tickets: int = 0
    won_notes: int = 0
    total: float = 0.0
    content: str = ""
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id, "lottery": self.lottery,
            "tickets": self.tickets, "won_notes": self.won_notes,
            "total": self.total, "created_at": self.created_at,
        }


class ReportCenter:
    """报告中心（本地 JSON）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "prize_reports.json")
        self._reports: dict = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                for rid, d in data.items():
                    self._reports[rid] = PrizeReport(**{k: v for k, v in d.items() if k in PrizeReport.__dataclass_fields__})
            except (json.JSONDecodeError, OSError):
                self._reports = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({rid: r.to_dict() for rid, r in self._reports.items()}, f, ensure_ascii=False, indent=2)

    def save(self, lottery: str, tickets: int, won_notes: int, total: float, content: str) -> PrizeReport:
        rid = f"R-{len(self._reports) + 1:04d}"
        while rid in self._reports:
            rid = f"R-{len(self._reports) + 1:04d}"
        r = PrizeReport(report_id=rid, lottery=lottery, tickets=tickets,
                        won_notes=won_notes, total=total, content=content)
        self._reports[rid] = r
        self._save()
        return r

    def get(self, report_id: str) -> Optional[PrizeReport]:
        return self._reports.get(report_id)

    def list_all(self) -> List[PrizeReport]:
        return sorted(self._reports.values(), key=lambda r: r.created_at, reverse=True)

    def by_lottery(self, lottery: str) -> List[PrizeReport]:
        return [r for r in self.list_all() if r.lottery == lottery]

    def count(self) -> int:
        return len(self._reports)

    def total_winnings(self) -> float:
        return sum(r.total for r in self._reports.values())

    def clear(self) -> None:
        self._reports = {}
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
