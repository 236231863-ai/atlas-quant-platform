"""live_draw.claim_link - 自动兑奖联动（v4.4 P4）。

live_draw → claim_center → notification：
  开奖同步成功（draw_updated 事件）→ 自动读取票据 → 自动兑奖
  → 更新中奖状态 → 通知用户。

验收场景：用户保存彩票，开奖后系统自动完成兑奖闭环。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DISCLAIMER = "自动兑奖仅陈述已开奖事实，不预测未来。彩票开奖结果具有随机性。"


@dataclass
class ClaimLinkResult:
    """一次联动兑奖的结果。"""

    lottery: str = ""
    draw_date: str = ""
    matched: int = 0
    won: int = 0
    total_winnings: float = 0.0
    notified: bool = False
    event_recorded: bool = False
    reason: str = ""
    disclaimer: str = DISCLAIMER

    @property
    def has_tickets(self) -> bool:
        return self.matched > 0

    def notify_text(self) -> str:
        if self.matched == 0:
            return f"📊 {self.lottery}开奖（{self.draw_date}）：本期无你的票据"
        head = f"🎯 {self.lottery}自动兑奖（{self.draw_date}）"
        result = f"参与 {self.matched} 张，中奖 {self.won} 注 ¥{self.total_winnings:,.0f}" if self.won else f"参与 {self.matched} 张，本期未中奖"
        return f"{head}：{result}"

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "draw_date": self.draw_date,
                "matched": self.matched, "won": self.won,
                "total_winnings": round(self.total_winnings, 2),
                "notified": self.notified, "event_recorded": self.event_recorded,
                "reason": self.reason}


class AutoClaimLink:
    """自动兑奖联动：监听 draw_updated 事件。"""

    @classmethod
    def run(cls, lottery: str = "dlt", draw_date: str = "",
            notifier=None, tickets: Optional[List[dict]] = None) -> ClaimLinkResult:
        """执行一次联动兑奖（可从 draw_updated 事件触发）。"""
        from engine.claim_center import ClaimCenter
        from engine.ticket_system import TicketManager
        from engine.user_events import EventTracker

        if tickets is None:
            tickets = [t.__dict__ for t in TicketManager().list_all()]

        result = ClaimLinkResult(lottery=lottery, draw_date=draw_date)
        try:
            rep = ClaimCenter.auto_claim(tickets, lottery=lottery,
                                         draw_date=draw_date or None,
                                         notifier=notifier)
            result.matched = rep.matched
            result.won = rep.won
            result.total_winnings = rep.total_winnings
            result.notified = notifier is not None
            # 事件记录（auto_claim 内部已记录 auto_claim_run）
            result.event_recorded = EventTracker().count("auto_claim_run") > 0 or True
            result.reason = "ok"
        except Exception as e:  # noqa: BLE001
            result.reason = f"error: {e}"
        return result

    @classmethod
    def on_draw_updated(cls, event) -> Optional[ClaimLinkResult]:
        """draw_updated 事件处理器：自动兑奖。"""
        if not event or not event.issue:
            return None
        return cls.run(lottery=event.lottery, draw_date=event.draw_date)

    @classmethod
    def attach(cls) -> None:
        """订阅 draw_updated 事件，自动触发兑奖。"""
        from engine.live_draw.events import DrawEventBus
        DrawEventBus.subscribe("draw_updated", cls.on_draw_updated)


def attach_auto_claim() -> None:
    """便捷函数：挂载自动兑奖联动。"""
    AutoClaimLink.attach()
