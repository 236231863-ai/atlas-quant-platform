"""ticket_system - 日期意图解析器（v3.8.0 日期升级 Phase 1）。

语义识别购买日期/开奖日期，支持相对日期（昨天/今天/前天）。
输出：{purchase_date, draw_date}（YYYY-MM-DD）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass
class DateIntent:
    """日期意图解析结果。"""

    purchase_date: Optional[str] = None
    draw_date: Optional[str] = None
    has_purchase: bool = False
    has_draw: bool = False
    need_confirm: bool = False  # 仅购买日期无开奖 → 需确认

    def to_dict(self) -> dict:
        return {"purchase_date": self.purchase_date, "draw_date": self.draw_date}


def _parse_abs_date(text: str) -> Optional[str]:
    """解析绝对日期：2026-07-31 / 7月31日 / 7/31 / 2026年7月31日。返回 YYYY-MM-DD。"""
    m = re.search(r"(20\d{2})[年\-/](\d{1,2})[月\-/](\d{1,2})", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r"(\d{1,2})月(\d{1,2})日?", text)
    if m:
        year = date.today().year
        return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.search(r"(\d{1,2})/(\d{1,2})", text)
    if m:
        year = date.today().year
        return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return None


def _relative_date(text: str) -> Optional[str]:
    """相对日期：昨天/今天/前天。"""
    today = date.today()
    if "昨天" in text:
        return (today - timedelta(days=1)).isoformat()
    if "前天" in text:
        return (today - timedelta(days=2)).isoformat()
    if "今天" in text or "今日" in text:
        return today.isoformat()
    return None


_DATE_RE = re.compile(
    r"(20\d{2})[年\-/](\d{1,2})[月\-/](\d{1,2})"
    r"|(\d{1,2})月(\d{1,2})日?"
    r"|(\d{1,2})/(\d{1,2})"
)


def _all_dates(section: str) -> list:
    """提取 section 中所有日期（YYYY-MM-DD），按出现顺序。"""
    out = []
    for m in _DATE_RE.finditer(section):
        if m.group(1):
            out.append(f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}")
        elif m.group(4):
            out.append(f"{date.today().year}-{int(m.group(4)):02d}-{int(m.group(5)):02d}")
        elif m.group(6):
            out.append(f"{date.today().year}-{int(m.group(6)):02d}-{int(m.group(7)):02d}")
    return out


class DateIntentParser:
    """日期意图解析器。"""

    @staticmethod
    def parse(text: str) -> DateIntent:
        """识别购买日期与开奖日期。

        规则：
          - 出现日期 + "买/购买/购彩" → 购买日期
          - 出现日期 + "开奖/开" → 开奖日期
          - 相对日期（昨天等）→ 购买日期
          - 仅一个日期且无明显语义 → 优先视为购买日期
        """
        r = DateIntent()
        if not text:
            return r
        # 定位购买/开奖关键词附近的日期
        buy_match = re.search(r"([^。；;]*?(?:买|购买|购彩)[^。；;]*)", text)
        draw_match = re.search(r"([^。；;]*?开奖[^。；;]*)", text)

        # 购买取第一个日期；开奖取「开奖」前最近日期（避免误取购买日）
        buy_date = None
        draw_date = None
        if buy_match:
            dates = _all_dates(buy_match.group(1))
            buy_date = dates[0] if dates else _relative_date(buy_match.group(1))
        if draw_match:
            dates = _all_dates(draw_match.group(1))
            draw_date = dates[-1] if dates else _relative_date(draw_match.group(1))

        # 兜底：无关键词时，第一个日期=购买，第二个=开奖
        if buy_date is None and draw_date is None:
            dates = [d for d in [_parse_abs_date(text), _relative_date(text)] if d]
            if dates:
                buy_date = dates[0]
                if len(dates) > 1:
                    draw_date = dates[1]

        r.purchase_date = buy_date
        r.draw_date = draw_date
        r.has_purchase = bool(buy_date)
        r.has_draw = bool(draw_date)
        # 仅购买无开奖 → 需确认
        r.need_confirm = bool(buy_date) and not draw_date
        return r
