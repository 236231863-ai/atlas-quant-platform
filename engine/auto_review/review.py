"""auto_review - 自动复盘系统（v4.2 Phase 2）。

开奖后主动告诉用户结果：
  开奖 → 自动匹配票据 → 生成结果报告

例如：
  「你的3张大乐透已开奖」「本期未中奖」「本月累计投入120元」「历史中奖2次」

红线：只陈述已发生的事实，禁止诱导购彩 / 预测。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

DISCLAIMER = "复盘仅陈述已开奖事实，不预测未来。彩票开奖结果具有随机性。"

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}
LOTTERIES = [("dlt", "大乐透"), ("ssq", "双色球")]


@dataclass
class AutoReviewReport:
    """一期自动复盘报告。"""

    lottery: str = "dlt"
    lottery_name: str = "大乐透"
    draw_date: str = ""
    draw_issue: str = ""
    draw_front: List[int] = field(default_factory=list)
    draw_back: List[int] = field(default_factory=list)
    ticket_count: int = 0               # 本期参与张数
    win_tickets: int = 0                # 本期中奖张数
    total_stake: float = 0.0            # 本期投入
    total_winnings: float = 0.0         # 本期中奖
    month_investment: float = 0.0       # 本月累计投入（全部彩种）
    history_win_count: int = 0          # 历史中奖次数（全部彩种）
    per_ticket: List[dict] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def participated(self) -> bool:
        return self.ticket_count > 0

    @property
    def any_win(self) -> bool:
        return self.total_winnings > 0

    def to_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "lottery_name": self.lottery_name,
            "draw_date": self.draw_date,
            "draw_issue": self.draw_issue,
            "draw_front": list(self.draw_front),
            "draw_back": list(self.draw_back),
            "ticket_count": self.ticket_count,
            "win_tickets": self.win_tickets,
            "total_stake": round(self.total_stake, 2),
            "total_winnings": round(self.total_winnings, 2),
            "month_investment": round(self.month_investment, 2),
            "history_win_count": self.history_win_count,
            "per_ticket": list(self.per_ticket),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        """完整复盘报告文本。"""
        lines = [f"📊 {self.lottery_name}自动复盘（{self.draw_date}）"]
        if not self.participated:
            lines.append("· 本期没有你的票据")
            lines.append(f"· 开奖号码：{' '.join(f'{n:02d}' for n in self.draw_front)}"
                         f" + {' '.join(f'{n:02d}' for n in self.draw_back)}")
            lines.append(f"· {self.disclaimer}")
            return "\n".join(lines)
        lines.append(f"· 参与票据：{self.ticket_count} 张（投入 ¥{self.total_stake:,.0f}）")
        if self.any_win:
            lines.append(f"· 本期中奖 {self.win_tickets} 注，合计 ¥{self.total_winnings:,.0f}")
        else:
            lines.append("· 本期未中奖")
        lines.append(f"· 本月累计投入：¥{self.month_investment:,.0f}")
        lines.append(f"· 历史中奖次数：{self.history_win_count} 次")
        for i, t in enumerate(self.per_ticket[:10], 1):
            mark = "✅" if t["won"] else "—"
            lines.append(f"  {i}. {mark} {' '.join(f'{n:02d}' for n in t['front'])}"
                         f" + {' '.join(f'{n:02d}' for n in t['back'])}"
                         f"（中{t['amount']:,.0f}）")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)

    def notify_text(self) -> str:
        """桌面通知短文案。"""
        head = f"你的{self.ticket_count}张{self.lottery_name}已开奖"
        if self.any_win:
            result = f"本期中奖{self.win_tickets}注，合计¥{self.total_winnings:,.0f}"
        else:
            result = "本期未中奖"
        month = f"本月累计投入¥{self.month_investment:,.0f}"
        hist = f"历史中奖{self.history_win_count}次"
        return "，".join([head, result, month, hist])


class AutoReviewEngine:
    """自动复盘引擎：开奖后自动匹配票据生成结果。"""

    @classmethod
    def _find_draw(cls, lottery: str, draw_date: Optional[str] = None):
        """查找开奖记录（缺省最近一期）。"""
        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        return DrawResultMatcher.find_draw(lottery, date=draw_date)

    @classmethod
    def _is_this_draw(cls, t: dict, lottery: str, draw_date: str) -> bool:
        """判断票据是否属于该期开奖。"""
        if t.get("lottery", "dlt") != lottery:
            return False
        # 显式 draw_date 匹配
        if t.get("draw_date"):
            return t["draw_date"] == draw_date
        # 无 draw_date → 按购买日推算最近开奖
        buy = t.get("buy_date") or t.get("saved_at", "")[:10]
        if buy:
            from engine.ticket_system.schedule import LotterySchedule
            try:
                nxt = LotterySchedule.next_draw_date(lottery, buy)
                return bool(nxt) and nxt == draw_date
            except Exception:
                return False
        return False

    @classmethod
    def _month_investment(cls, tickets: List[dict]) -> float:
        today = date.today()
        total = 0.0
        for t in tickets:
            d = t.get("buy_date") or t.get("saved_at", "")[:10]
            if d and len(d) == 10 and d.startswith(f"{today.year}-{today.month:02d}"):
                total += float(t.get("cost", 2.0))
        return total

    @classmethod
    def _history_win_count(cls, tickets: List[dict]) -> int:
        from engine.personal_review import PersonalReviewEngine
        try:
            return PersonalReviewEngine.review(tickets).win_count
        except Exception:
            return 0

    @classmethod
    def build(cls, tickets: List[dict], lottery: str = "dlt",
              draw_date: Optional[str] = None) -> AutoReviewReport:
        """构建一期自动复盘。"""
        draw = cls._find_draw(lottery, draw_date)
        if draw is None:
            return AutoReviewReport(lottery=lottery,
                                    lottery_name=LOTTERY_NAMES.get(lottery, lottery))
        d = draw.draw_date
        rep = AutoReviewReport(lottery=lottery,
                               lottery_name=LOTTERY_NAMES.get(lottery, lottery),
                               draw_date=d,
                               draw_issue=draw.number,
                               draw_front=list(draw.front),
                               draw_back=list(draw.back))

        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator
        matcher = DrawResultMatcher()
        for t in tickets:
            if not cls._is_this_draw(t, lottery, d):
                continue
            front = list(t.get("front", []))
            back = list(t.get("back", []))
            cost = float(t.get("cost", 2.0))
            rep.ticket_count += 1
            rep.total_stake += cost
            try:
                match = matcher.match(front, back, lottery=lottery, draw_date=d)
                if match.draw:
                    pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, lottery)
                    won = pr.won
                    amount = pr.amount if won else 0.0
                else:
                    won, amount = False, 0.0
            except Exception:
                won, amount = False, 0.0
            if won:
                rep.win_tickets += 1
                rep.total_winnings += amount
            rep.per_ticket.append({"front": front, "back": back, "won": won, "amount": amount})

        rep.month_investment = cls._month_investment(tickets)
        rep.history_win_count = cls._history_win_count(tickets)
        return rep

    @classmethod
    def check_draws(cls, tickets: List[dict]) -> List[AutoReviewReport]:
        """自动检查所有彩种最近一期，返回有票据参与的复盘列表。

        用于「开奖后主动告诉用户」：有参与才生成报告，否则不打扰。
        """
        out = []
        for lottery, _ in LOTTERIES:
            rep = cls.build(tickets, lottery=lottery)
            if rep.participated:
                out.append(rep)
        return out

    @classmethod
    def build_from_manager(cls, lottery: str = "dlt",
                           draw_date: Optional[str] = None) -> AutoReviewReport:
        """从 TicketManager 读取票据复盘。"""
        from engine.ticket_system import TicketManager
        tickets = [t.__dict__ for t in TicketManager().list_all()]
        return cls.build(tickets, lottery=lottery, draw_date=draw_date)


def auto_review(tickets: List[dict], lottery: str = "dlt",
                draw_date: Optional[str] = None) -> AutoReviewReport:
    """便捷函数：自动复盘。"""
    return AutoReviewEngine.build(tickets, lottery=lottery, draw_date=draw_date)
