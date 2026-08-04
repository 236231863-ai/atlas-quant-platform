"""behavior_analysis.analysis - 用户投注历史分析引擎（v4.7 P1）。

读取 ticket_system 历史票据，生成用户投注画像：
  总投入 / 总中奖 / 净收益 / ROI / 平均每期投入 / 中奖次数 /
  中奖等级分布 / 最大亏损周期 / 连续未中奖 / 投注频率

真实数据驱动（不预测）。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

DISCLAIMER = "分析基于你的真实投注历史。彩票开奖结果具有随机性，任何号码组合理论中奖概率相同。"

PRIZE_LEVELS = ("一等奖", "二等奖", "三等奖", "四等奖", "五等奖", "六等奖",
                "七等奖", "八等奖", "九等奖")


@dataclass
class UserBehaviorReport:
    """用户投注画像。"""

    total_tickets: int = 0
    total_investment: float = 0.0
    total_winnings: float = 0.0
    win_count: int = 0
    prize_dist: Dict[str, int] = field(default_factory=dict)
    max_loss_streak: int = 0
    current_loss_streak: int = 0
    bet_frequency: float = 0.0       # 期/月
    avg_per_bet: float = 0.0
    first_bet_date: str = ""
    last_bet_date: str = ""
    disclaimer: str = DISCLAIMER

    @property
    def net(self) -> float:
        return self.total_winnings - self.total_investment

    @property
    def roi(self) -> float:
        if self.total_investment <= 0:
            return 0.0
        return self.net / self.total_investment

    @property
    def win_rate(self) -> float:
        if self.total_tickets == 0:
            return 0.0
        return self.win_count / self.total_tickets

    def to_dict(self) -> dict:
        return {"total_tickets": self.total_tickets,
                "total_investment": round(self.total_investment, 2),
                "total_winnings": round(self.total_winnings, 2),
                "net": round(self.net, 2), "roi": round(self.roi, 4),
                "win_count": self.win_count, "win_rate": round(self.win_rate, 4),
                "prize_dist": dict(self.prize_dist),
                "max_loss_streak": self.max_loss_streak,
                "current_loss_streak": self.current_loss_streak,
                "bet_frequency": round(self.bet_frequency, 2),
                "avg_per_bet": round(self.avg_per_bet, 2),
                "first_bet_date": self.first_bet_date,
                "last_bet_date": self.last_bet_date}

    def summary_text(self) -> str:
        lines = ["📊 我的投注画像"]
        lines.append(f"· 总投入：¥{self.total_investment:,.0f}（{self.total_tickets} 注）")
        lines.append(f"· 总中奖：¥{self.total_winnings:,.0f} · 中奖 {self.win_count} 次")
        lines.append(f"· 净收益：¥{self.net:,.0f} · ROI {self.roi * 100:.1f}%")
        lines.append(f"· 平均每期投入：¥{self.avg_per_bet:,.0f} · 投注频率：{self.bet_frequency:.1f} 期/月")
        lines.append(f"· 最大亏损周期：{self.max_loss_streak} 期 · 当前连续未中：{self.current_loss_streak} 期")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class BehaviorAnalyzer:
    """投注行为分析器。"""

    @classmethod
    def _win_info(cls, t: dict) -> tuple:
        """单张票据中奖等级与金额。"""
        try:
            from engine.lottery_intent.draw_matcher import DrawResultMatcher
            from engine.lottery_intent.prize_calculator import PrizeCalculator
            match = DrawResultMatcher().match(
                list(t.get("front", [])), list(t.get("back", [])),
                lottery=t.get("lottery", "dlt"), draw_date=t.get("draw_date", ""))
            if not match.draw:
                return None, 0.0
            pr = PrizeCalculator.calculate(match.front_hits, match.back_hits,
                                           t.get("lottery", "dlt"))
            if pr.won:
                return pr.level_name if hasattr(pr, "level_name") else "中奖", pr.amount
            return None, 0.0
        except Exception:
            return None, 0.0

    @classmethod
    def build(cls, tickets: List[dict]) -> UserBehaviorReport:
        """从票据构建投注画像（票据按 buy_date 排序）。"""
        rep = UserBehaviorReport()
        if not tickets:
            return rep

        rep.total_tickets = len(tickets)
        rep.total_investment = sum(float(t.get("cost", 2.0)) for t in tickets)
        rep.avg_per_bet = rep.total_investment / rep.total_tickets

        # 按购买日期排序
        sorted_tickets = sorted(tickets, key=lambda t: t.get("buy_date") or t.get("saved_at", ""))
        dates = [t.get("buy_date") or t.get("saved_at", "")[:10] for t in sorted_tickets]
        rep.first_bet_date = next((d for d in dates if d), "")
        rep.last_bet_date = next((d for d in reversed(dates) if d), "")

        # 中奖统计 + 连续未中
        loss_streak = 0
        max_loss = 0
        cur_loss = 0
        for t in sorted_tickets:
            level, amount = cls._win_info(t)
            if level:
                rep.win_count += 1
                rep.total_winnings += amount
                rep.prize_dist[level] = rep.prize_dist.get(level, 0) + 1
                loss_streak = 0
                cur_loss = 0
            else:
                loss_streak += 1
                cur_loss += 1
                max_loss = max(max_loss, loss_streak)
        rep.max_loss_streak = max_loss
        rep.current_loss_streak = cur_loss

        # 投注频率：期/月（按跨度）
        rep.bet_frequency = cls._frequency(dates, rep.total_tickets)
        return rep

    @staticmethod
    def _frequency(dates: List[str], total: int) -> float:
        """投注频率（期/月）。"""
        valid = [d for d in dates if d and len(d) == 10]
        if not valid or total == 0:
            return 0.0
        months = {}
        for d in valid:
            months[d[:7]] = months.get(d[:7], 0) + 1
        span = max(1, len(months))
        return total / span


def build_behavior_analysis(tickets: List[dict]) -> UserBehaviorReport:
    """便捷函数。"""
    return BehaviorAnalyzer.build(tickets)
