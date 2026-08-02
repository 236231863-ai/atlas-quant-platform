"""lottery_intent - 彩票号码解析（TicketParser）。

从用户自然语言中提取：
  - 购买日期 / 开奖日期
  - 前区号码 / 后区号码（支持多注）
  - 彩种推断（号码特征）

支持输入格式示例：
  "7月31日买了 01 02 03 04 05 + 06 07"
  "前区 01 02 03 04 05 后区 06 07"
  "05,10,15,20,25|08,09"
  "注1: 01 02 03 04 05 + 06 07；注2: ..."
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

# 日期模式：7月31日 / 2026-07-31 / 7/31 / 8月1日
_DATE_PATTERNS = [
    re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日?"),
    re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"),
    re.compile(r"(\d{1,2})/(\d{1,2})"),
]


@dataclass
class Ticket:
    """一张彩票（一注）。"""

    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.front) >= 3 and len(self.back) >= 1


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
                    # 7月31日 或 7/31 → 当年
                    if "月" in m.group(0):
                        dates.append(f"{int(g[0]):02d}-{int(g[1]):02d}")
                    else:
                        dates.append(f"{int(g[0]):02d}-{int(g[1]):02d}")
        # 购买日期通常在"买了/买了这些"附近；开奖日期在"开奖"附近
        buy = ""
        draw = ""
        for d in dates:
            # 简单启发：买(前面) vs 开奖(后面)
            pass
        if len(dates) >= 1:
            buy = dates[0]
        if len(dates) >= 2:
            draw = dates[1]
        return {"buy": buy, "draw": draw}

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
        """解析用户输入的号码。"""
        result = TicketParseResult()
        if not text:
            return result
        dates = cls._extract_dates(text)
        result.buy_date = dates["buy"]
        result.draw_date = dates["draw"]

        # 提取号码段：前区（front）+ 后区（back）
        # 支持分隔符 | + 或 前后区关键词
        for note in cls._split_notes(text):
            front, back = cls._extract_numbers(note)
            if front and back:
                t = Ticket(front=front, back=back)
                result.tickets.append(t)
                if not result.lottery:
                    result.lottery = cls._infer_lottery(front, back)
        result.parsed_notes = len(result.tickets)
        return result

    @staticmethod
    def _extract_numbers(note: str) -> tuple:
        """从一段文本提取 (front_numbers, back_numbers)。"""
        # 用 | 分隔
        if "|" in note:
            f_part, b_part = note.split("|", 1)
        elif "+" in note:
            f_part, b_part = note.split("+", 1)
        else:
            # 找"后区"关键词或末尾数字
            m = re.search(r"后区[:：]?\s*([\d\s,]+)", note)
            if m:
                f_part = note[: m.start()]
                b_part = m.group(1)
            else:
                nums = [int(x) for x in re.findall(r"\d{1,2}", note)]
                return nums[:5], nums[5:7]
        f_nums = [int(x) for x in re.findall(r"\d{1,2}", f_part)]
        b_nums = [int(x) for x in re.findall(r"\d{1,2}", b_part)]
        return f_nums, b_nums
