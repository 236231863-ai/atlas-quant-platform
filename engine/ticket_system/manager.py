"""ticket_system - 票据管理。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class TicketRecord:
    """一张已保存的票据。"""

    ticket_id: str
    lottery: str = "dlt"
    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)
    buy_date: str = ""
    draw_date: str = ""
    cost: float = 2.0
    saved_at: str = field(default_factory=_now)
    claimed: bool = False

    def to_text(self) -> str:
        return (f"[{self.ticket_id}] {self.lottery} "
                f"{' '.join(f'{n:02d}' for n in self.front)} + {' '.join(f'{n:02d}' for n in self.back)}"
                f" 买{self.buy_date} 开{self.draw_date}")


class TicketManager:
    """票据管理器（本地 JSON）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "tickets_v2.json")
        self._tickets: dict = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                for tid, d in data.items():
                    self._tickets[tid] = TicketRecord(**{k: v for k, v in d.items() if k in TicketRecord.__dataclass_fields__})
            except (json.JSONDecodeError, OSError):
                self._tickets = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({tid: t.__dict__ for tid, t in self._tickets.items()}, f, ensure_ascii=False, indent=2)

    def add(self, lottery: str, front: List[int], back: List[int],
            buy_date: str = "", draw_date: str = "", cost: float = 2.0) -> TicketRecord:
        tid = f"T-{len(self._tickets) + 1:04d}"
        while tid in self._tickets:
            tid = f"T-{len(self._tickets) + 1:04d}"
        t = TicketRecord(ticket_id=tid, lottery=lottery, front=front, back=back,
                         buy_date=buy_date, draw_date=draw_date, cost=cost)
        self._tickets[tid] = t
        self._save()
        return t

    def add_from_text(self, text: str) -> List[TicketRecord]:
        """从自然语言解析并保存票据（复用 TicketParser）。"""
        from engine.lottery_intent.ticket_parser import TicketParser
        from engine.lottery_intent.intent_router import LotteryIntentRouter
        intent = LotteryIntentRouter.detect(text)
        parse = TicketParser.parse(text)
        lottery = intent.lottery or parse.lottery or "dlt"
        saved = []
        for t in parse.tickets:
            saved.append(self.add(lottery, t.front, t.back,
                                  buy_date=parse.buy_date, draw_date=parse.draw_date))
        return saved

    def get(self, ticket_id: str) -> Optional[TicketRecord]:
        return self._tickets.get(ticket_id)

    def list_all(self) -> List[TicketRecord]:
        return list(self._tickets.values())

    def by_lottery(self, lottery: str) -> List[TicketRecord]:
        return [t for t in self._tickets.values() if t.lottery == lottery]

    def count(self) -> int:
        return len(self._tickets)

    def set_claimed(self, ticket_id: str, claimed: bool = True) -> bool:
        """v4.3 P2：标记票据已兑奖（持久化）。"""
        if ticket_id in self._tickets:
            self._tickets[ticket_id].claimed = claimed
            self._save()
            return True
        return False

    def delete(self, ticket_id: str) -> bool:
        if ticket_id in self._tickets:
            del self._tickets[ticket_id]
            self._save()
            return True
        return False

    def clear(self) -> None:
        self._tickets = {}
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
