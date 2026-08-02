"""lottery_intent - 彩票号码解析（TicketParser，v3.8.2-P1 Phase 2）。

从用户自然语言中提取：
  - 购买日期 / 开奖日期
  - 前区号码 / 后区号码（支持多注：15/30/100 注）
  - 彩种推断（号码特征）

v3.8.2-P1 新增能力：
  - 连续号码串解析：13212326330112 → 13 21 23 26 33 + 01 12
  - 多注连续串（每注 5 前区 + 2 后区 = 14 位数字）自动切分
  - 日期与号码隔离（避免把 "7月31日" 的 7/31 误当号码）

支持输入格式示例：
  "7月31日买了 01 02 03 04 05 + 06 07"
  "前区 01 02 03 04 05 后区 06 07"
  "05,10,15,20,25|08,09"
  "13212326330112"                        ← 连续号码（1 注）
  "13212326330112 01020304050607"         ← 连续号码（2 注，每注 14 位）
  "注1: 01 02 03 04 05 + 06 07；注2: ..."
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# 日期模式：7月31日 / 2026-07-31 / 7/31 / 8月1日
_DATE_PATTERNS = [
    re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"),
    re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日?"),
    re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)"),
]

# 大乐透每注数字数（前 5 + 后 2 = 7 个），双色球同样 7 个（前 6 + 后 1）
NOTE_DIGIT_COUNT = 7


@dataclass
class Ticket:
    """一张彩票（一注）。"""

    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.front) >= 3 and len(self.back) >= 1

    def to_dict(self) -> dict:
        return {"front": list(self.front), "back": list(self.back)}


@dataclass
class TicketParseResult:
    """解析结果。"""

    tickets: List[Ticket] = field(default_factory=list)
    buy_date: str = ""       # 购买日期
    draw_date: str = ""      # 开奖日期
    lottery: str = ""        # 推断彩种
    parsed_notes: int = 0

    @property
    def is_viable(self) -> bool:
        return len(self.tickets) > 0

    def to_ticket_dicts(self) -> List[dict]:
        """输出 [{front, back}]，供 PendingTask 保存。"""
        return [t.to_dict() for t in self.tickets]


class TicketParser:
    """号码解析器。"""

    @staticmethod
    def _extract_dates(text: str) -> dict:
        dates = []
        for pat in _DATE_PATTERNS:
            for m in pat.finditer(text):
                g = m.groups()
                if len(g) == 3:  # 2026-07-31
                    dates.append(f"{int(g[0]):04d}-{int(g[1]):02d}-{int(g[2]):02d}")
                elif len(g) == 2:
                    dates.append(f"{int(g[0]):02d}-{int(g[1]):02d}")
        # 购买日期通常在"买了/买了这些"附近；开奖日期在"开奖"附近
        buy = ""
        draw = ""
        if len(dates) >= 1:
            buy = dates[0]
        if len(dates) >= 2:
            draw = dates[1]
        return {"buy": buy, "draw": draw}

    @staticmethod
    def _strip_dates(text: str) -> str:
        """移除日期片段，避免日期数字混入号码解析。"""
        out = text
        for pat in _DATE_PATTERNS:
            out = pat.sub("", out)
        return out

    @staticmethod
    def _infer_lottery(front: List[int], back: List[int]) -> str:
        # 大乐透：前区5 后区2（1-35,1-12）；双色球：前区6 后区1（1-33,1-16）
        if len(front) == 6 and len(back) == 1:
            return "ssq"
        if len(front) == 5 and len(back) == 2:
            return "dlt"
        return ""

    @staticmethod
    def _split_notes(text: str) -> List[str]:
        """按分号/换行/注 拆分多注。"""
        text = re.sub(r"[；;]", "\n", text)
        text = re.sub(r"注\d*\s*[:：]", "\n", text)
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        return parts or [text]

    @classmethod
    def parse(cls, text: str) -> TicketParseResult:
        """解析用户输入的号码（v3.8.2-P1：支持连续号码串与多注）。"""
        result = TicketParseResult()
        if not text:
            return result
        dates = cls._extract_dates(text)
        result.buy_date = dates["buy"]
        result.draw_date = dates["draw"]

        # 去掉日期后再拆注，避免 "7月31日" 的数字干扰
        clean = cls._strip_dates(text)
        for note in cls._split_notes(clean):
            for front, back in cls._parse_note(note):
                if front and back:
                    t = Ticket(front=front, back=back)
                    result.tickets.append(t)
                    if not result.lottery:
                        result.lottery = cls._infer_lottery(front, back)
        result.parsed_notes = len(result.tickets)
        return result

    # ---------- v3.8.2-P1：连续号码解析 ----------
    @staticmethod
    def _extract_all_numbers(note: str) -> List[int]:
        """提取一段文本中的所有 1-2 位数字（连续串按两位贪婪切分）。"""
        return [int(x) for x in re.findall(r"\d{1,2}", note)]

    @classmethod
    def _parse_note(cls, note: str) -> List[Tuple[List[int], List[int]]]:
        """解析一段文本为一注或多注 (front, back)。

        策略：
          1. 含 +/|/后区 分隔 → 单注传统解析
          2. 纯数字 → 按每注 7 个数字切分（5 前区 + 2 后区，v3.8.2-P1）
          3. 兜底：前 5 后 2

        注意：先移除量词数字（"15组/30注/100期"），避免注数混入号码。
        """
        note = note.strip()
        if not note:
            return []

        # 移除量词数字：15组 / 30注 / 100期 / 2倍（注数描述，非号码）
        note = re.sub(r"\d{1,3}\s*(?:组|注|个|期|倍)", "", note)

        # 1) 传统分隔符（+ / | / 后区）→ 单注
        if "|" in note or "+" in note or "后区" in note:
            m = re.search(r"后区[:：]?\s*([\d\s,]+)", note)
            if m:
                f_part = note[: m.start()]
                b_part = m.group(1)
            elif "|" in note:
                f_part, b_part = note.split("|", 1)
            else:
                f_part, b_part = note.split("+", 1)
            f_nums = cls._extract_all_numbers(f_part)
            b_nums = cls._extract_all_numbers(b_part)
            if f_nums and b_nums:
                return [(f_nums, b_nums)]
            return []

        # 2) 纯数字（含空格分隔的多注）
        nums = cls._extract_all_numbers(note)
        if not nums:
            return []

        n = len(nums)
        # 多注：数字总数为 7 的倍数 → 每 7 个一组（前 5 后 2）
        if n >= NOTE_DIGIT_COUNT and n % NOTE_DIGIT_COUNT == 0:
            notes = []
            for i in range(0, n, NOTE_DIGIT_COUNT):
                group = nums[i:i + NOTE_DIGIT_COUNT]
                notes.append((group[:5], group[5:7]))
            return notes

        # 3) 兜底：前 5 后 2
        if n >= 7:
            return [(nums[:5], nums[5:7])]
        return []
