"""user_archive - 个人彩票档案（v4.2 Phase 1 用户数据中心）。

让用户拥有自己的彩票档案：
  累计购买 / 累计中奖 / 中奖次数 / 最高奖金 / 购买周期 / 常购彩种

档案是中性个人记录：只反映历史购彩与中奖数据，不预测、不诱导购彩。
"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

DISCLAIMER = "档案记录你的历史购彩与中奖数据，不预测未来。彩票开奖结果具有随机性。"

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class LotteryArchive:
    """个人彩票档案（v4.2 Phase 1）。"""

    total_tickets: int = 0
    total_investment: float = 0.0        # 累计购买 ¥
    total_winnings: float = 0.0          # 累计中奖 ¥
    win_count: int = 0                   # 中奖次数
    max_win: float = 0.0                 # 最高奖金 ¥
    purchase_months: int = 0             # 购买周期（月）
    favorite_lotteries: List[str] = field(default_factory=list)  # 常购彩种
    lottery_dist: dict = field(default_factory=dict)             # {彩种名: 张数}
    first_buy_date: str = ""
    last_buy_date: str = ""
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "total_tickets": self.total_tickets,
            "total_investment": round(self.total_investment, 2),
            "total_winnings": round(self.total_winnings, 2),
            "win_count": self.win_count,
            "max_win": round(self.max_win, 2),
            "purchase_months": self.purchase_months,
            "favorite_lotteries": list(self.favorite_lotteries),
            "lottery_dist": dict(self.lottery_dist),
            "first_buy_date": self.first_buy_date,
            "last_buy_date": self.last_buy_date,
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        """档案文本（个人中心展示）。"""
        lines = ["🗂 我的彩票档案"]
        lines.append(f"· 累计购买：¥{self.total_investment:,.0f}")
        lines.append(f"· 累计中奖：¥{self.total_winnings:,.0f}")
        lines.append(f"· 中奖次数：{self.win_count} 次")
        lines.append(f"· 最高奖金：¥{self.max_win:,.0f}")
        lines.append(f"· 购买周期：{self.purchase_months} 个月")
        if self.favorite_lotteries:
            lines.append("· 常购彩种：" + " / ".join(self.favorite_lotteries))
        if self.first_buy_date and self.last_buy_date:
            lines.append(f"· 首购 {self.first_buy_date} → 最近 {self.last_buy_date}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class UserArchiveEngine:
    """个人彩票档案引擎。"""

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        if not date_str:
            return None
        try:
            if len(date_str) == 10:
                return date.fromisoformat(date_str)
            if len(date_str) == 5:
                return date.fromisoformat(f"{date.today().year}-{date_str}")
        except ValueError:
            return None
        return None

    @classmethod
    def _name(cls, lottery: str) -> str:
        return LOTTERY_NAMES.get(lottery, lottery)

    @classmethod
    def build(cls, tickets: List[dict]) -> LotteryArchive:
        """从票据列表构建个人档案。

        tickets: [{"lottery", "front", "back", "buy_date", "draw_date", "cost"}]
        """
        arch = LotteryArchive()
        if not tickets:
            return arch

        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator

        arch.total_tickets = len(tickets)
        arch.total_investment = sum(float(t.get("cost", 2.0)) for t in tickets)

        # 中奖统计
        matcher = DrawResultMatcher()
        for t in tickets:
            lottery = t.get("lottery", "dlt")
            front = list(t.get("front", []))
            back = list(t.get("back", []))
            draw_date = t.get("draw_date", "")
            purchase_date = t.get("buy_date", "") or t.get("saved_at", "")[:10]
            try:
                match = matcher.match(front, back, lottery=lottery,
                                      purchase_date=purchase_date or None,
                                      draw_date=draw_date or None)
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, lottery)
                    if pr.won:
                        arch.total_winnings += pr.amount
                        arch.win_count += 1
                        arch.max_win = max(arch.max_win, pr.amount)
            except Exception:
                continue

        # 购买周期（首购 → 最近购买，月份跨度）
        dates = []
        for t in tickets:
            d = cls._parse_date(t.get("buy_date") or t.get("saved_at", "")[:10])
            if d:
                dates.append(d)
        if dates:
            first = min(dates)
            last = max(dates)
            arch.first_buy_date = first.isoformat()
            arch.last_buy_date = last.isoformat()
            arch.purchase_months = (last.year - first.year) * 12 + (last.month - first.month) + 1

        # 常购彩种
        dist = Counter(cls._name(t.get("lottery", "dlt")) for t in tickets)
        arch.lottery_dist = dict(dist)
        arch.favorite_lotteries = [name for name, _ in dist.most_common(2)]

        return arch

    @classmethod
    def build_from_manager(cls, ticket_manager=None) -> LotteryArchive:
        """从 TicketManager 读取票据构建档案。"""
        if ticket_manager is None:
            from engine.ticket_system import TicketManager
            ticket_manager = TicketManager()
        tickets = [t.__dict__ for t in ticket_manager.list_all()]
        return cls.build(tickets)


class ArchiveStore:
    """档案快照存储（~/.atlas/archive_v42.json，支持 ATLAS_STORAGE_DIR）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "archive_v42.json")

    def save(self, archive: LotteryArchive) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(archive.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self) -> Optional[dict]:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return None
        return None


def build_archive(tickets: List[dict]) -> LotteryArchive:
    """便捷函数：个人彩票档案。"""
    return UserArchiveEngine.build(tickets)
