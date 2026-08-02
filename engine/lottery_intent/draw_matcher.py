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
    """开奖结果匹配器（v3.8.0 日期升级 Phase 2）。

    匹配规则：
      - 有 draw_date → 精确匹配该日期的开奖（禁止穿越历史）
      - 只有 purchase_date → LotterySchedule 推算购买后最近开奖日 → 匹配
      - 都无 → 最新一期
    """

    @staticmethod
    def find_draw(lottery: str, date: Optional[str] = None, issue: Optional[str] = None) -> Optional[DrawRecord]:
        """按精确日期或期号查找开奖记录（日期精确匹配，防穿越）。"""
        mgr = DataSourceManager.from_project(lottery)
        draws = mgr.load()
        if issue:
            for d in draws:
                if d.number == str(issue):
                    return d
        if date:
            # 精确日期匹配（YYYY-MM-DD），禁止 substring（防穿越到 2024 年）
            target = date if len(date) == 10 else date
            for d in reversed(draws):
                if d.draw_date == target:
                    return d
            # 兼容 MM-DD 输入
            if len(date) == 5:
                for d in reversed(draws):
                    if d.draw_date[5:] == date:
                        return d
            # 指定日期未找到 → 返回 None（不落到最新，防误配）
            return None
        # 无日期 → 最新一期
        return draws[-1] if draws else None

    @classmethod
    def resolve_draw_date(cls, lottery: str, purchase_date: Optional[str] = None,
                          draw_date: Optional[str] = None) -> Optional[str]:
        """确定应匹配的开奖日期。

        优先 draw_date；否则用 LotterySchedule 由购买日推算最近开奖日。
        """
        if draw_date:
            return draw_date
        if purchase_date:
            from engine.ticket_system.schedule import LotterySchedule
            return LotterySchedule.next_draw_date(lottery, purchase_date)
        return None

    @classmethod
    def match(cls, ticket_front: List[int], ticket_back: List[int], lottery: str = "dlt",
              date: Optional[str] = None, issue: Optional[str] = None,
              purchase_date: Optional[str] = None, draw_date: Optional[str] = None) -> DrawMatch:
        """匹配一注号码与开奖结果（支持购买日/开奖日语义）。"""
        resolved = cls.resolve_draw_date(lottery, purchase_date=purchase_date, draw_date=draw_date or date)
        draw = cls.find_draw(lottery, date=resolved, issue=issue)
        if draw is None:
            return DrawMatch()
        fh = len(set(ticket_front) & set(draw.front))
        bh = len(set(ticket_back) & set(draw.back))
        return DrawMatch(draw=draw, front_hits=fh, back_hits=bh, matched=True)
