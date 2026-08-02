"""user_memory - 用户记忆与对话上下文。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChatContext:
    """对话上下文（连续对话理解）。"""

    last_numbers: str = ""          # 上次提到的号码
    last_lottery: str = ""          # 上次彩种
    last_intent: str = ""           # 上次意图
    history: List[str] = field(default_factory=list)  # 最近输入

    def remember(self, text: str) -> None:
        self.history.append(text)
        if len(self.history) > 6:
            self.history = self.history[-6:]

    def extract_numbers(self, text: str) -> str:
        """提取文本中的号码（用于无号码时回看上文）。"""
        from engine.lottery_intent.ticket_parser import TicketParser
        parse = TicketParser.parse(text)
        if parse.is_viable:
            return " ".join(f"{n:02d}" for t in parse.tickets for n in t.front + t.back)
        return ""


class UserMemory:
    """用户记忆（偏好持久化）。"""

    DEFAULTS = {"preferred_lottery": "dlt", "theme": "light", "last_page": "数据看板"}

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "user_memory.json")
        self._data: Dict[str, object] = dict(self.DEFAULTS)
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def set(self, key: str, value) -> None:
        self._data[key] = value
        self._save()

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set_preference(self, key: str, value) -> None:
        self._data[f"pref_{key}"] = value
        self._save()

    def get_preference(self, key: str, default=None):
        return self._data.get(f"pref_{key}", default)

    def preferred_lottery(self) -> str:
        return self.get("preferred_lottery", "dlt")

    def all(self) -> dict:
        return dict(self._data)

    def clear(self) -> None:
        self._data = dict(self.DEFAULTS)
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
