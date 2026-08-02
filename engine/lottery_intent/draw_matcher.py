"""lottery_intent - 开奖结果匹配（DrawResultMatcher）。

从数据源获取指定日期的开奖结果，并与用户号码匹配命中。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from engine.data_center_v2 import DataSourceManager, DrawRecord


@dataclass
class DrawMatch:
    """一次开奖匹配结果。"""

    draw: Optional[DrawRecord] = None
    front_hits: int = 0
    back_hits: int = 0
    matched: bool = False

    @property
    def hit_text(self) -> str:
        return f"前区中 {self.front_hits} 码 · 后区中 {self.back_hits} 码"


class DrawResultMatcher:
    """开奖结果匹配器。"""

    @staticmethod
    def find_draw(lottery: str, date: Optional[str] = None, issue: Optional[str] = None) -> Optional[DrawRecord]:
        """按日期或期号查找开奖记录。"""
        mgr = DataSourceManager.from_project(lottery)
        draws = mgr.load()
        if issue:
            for d in draws:
                if d.number == issue:
                    return d
        if date:
            # date 格式 YYYY-MM-DD 或 MM-DD
            for d in reversed(draws):
                if date in d.draw_date:
                    return d
        # 无日期 → 最新一期
        return draws[-1] if draws else None

    @classmethod
    def match(cls, ticket_front: List[int], ticket_back: List[int], lottery: str = "dlt",
              date: Optional[str] = None, issue: Optional[str] = None) -> DrawMatch:
        """匹配一注号码与开奖结果。"""
        draw = cls.find_draw(lottery, date=date, issue=issue)
        if draw is None:
            return DrawMatch()
        fh = len(set(ticket_front) & set(draw.front))
        bh = len(set(ticket_back) & set(draw.back))
        return DrawMatch(draw=draw, front_hits=fh, back_hits=bh, matched=True)
