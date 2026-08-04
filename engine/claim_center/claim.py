"""claim_center - 自动兑奖中心（v4.3 P2）。

用户无需主动询问：
  保存彩票 → 开奖 → 自动匹配 → 通知用户 → 生成兑奖报告

我的待兑奖列表（4 状态）：
  waiting_draw      等待开奖
  settled_unviewed  已开奖待查看
  viewed            已查看
  claimed           已兑奖

验收：所有关键步骤记录用户行为事件（ticket_saved / auto_claim_run /
      claim_viewed / claim_confirmed）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

DISCLAIMER = "自动兑奖仅陈述已开奖事实，不预测未来。彩票开奖结果具有随机性。"

CLAIM_STATUS = ("waiting_draw", "settled_unviewed", "viewed", "claimed")

STATUS_TEXT = {
    "waiting_draw": "等待开奖",
    "settled_unviewed": "已开奖待查看",
    "viewed": "已查看",
    "claimed": "已兑奖",
}


@dataclass
class ClaimItem:
    """一张票据的兑奖状态。"""

    ticket_id: str
    lottery: str = "dlt"
    front: List[int] = field(default_factory=list)
    back: List[int] = field(default_factory=list)
    draw_date: str = ""
    status: str = "waiting_draw"
    won: bool = False
    amount: float = 0.0

    @property
    def status_text(self) -> str:
        return STATUS_TEXT.get(self.status, self.status)

    def to_dict(self) -> dict:
        return {"ticket_id": self.ticket_id, "lottery": self.lottery,
                "front": list(self.front), "back": list(self.back),
                "draw_date": self.draw_date, "status": self.status,
                "status_text": self.status_text, "won": self.won,
                "amount": self.amount}


@dataclass
class AutoClaimReport:
    """一次自动兑奖报告（某期开奖）。"""

    lottery: str = "dlt"
    lottery_name: str = "大乐透"
    draw_date: str = ""
    matched: int = 0            # 参与张数
    won: int = 0                # 中奖张数
    total_winnings: float = 0.0
    unviewed: int = 0           # 待查看张数
    items: List[dict] = field(default_factory=list)
    disclaimer: str = DISCLAIMER
    # v4.5 P4：数据信任字段
    issue: str = ""             # 开奖期号
    data_source: str = "官方数据"  # 号码来源
    updated_at: str = ""        # 数据更新时间
    verified: bool = True       # 校验状态（已验证）

    @property
    def has_any(self) -> bool:
        return self.matched > 0

    def notify_text(self) -> str:
        head = f"📊 {self.lottery_name}自动兑奖（{self.draw_date}）"
        if self.matched == 0:
            return f"{head}：本期无你的票据"
        result = f"中奖 {self.won} 注 ¥{self.total_winnings:,.0f}" if self.won else "本期未中奖"
        return f"{head}：参与 {self.matched} 张，{result}"

    def summary_text(self) -> str:
        lines = [self.notify_text()]
        for it in self.items[:10]:
            mark = "✅" if it.get("won") else "—"
            lines.append(f"  {mark} {it.get('ticket_id', '票')} "
                         f"{' '.join(f'{n:02d}' for n in it.get('front', []))} + "
                         f"{' '.join(f'{n:02d}' for n in it.get('back', []))}"
                         f"（{it.get('status_text', '')}）")
        # v4.5 P4：兑奖信任信息
        lines.append(f"· 数据来源：{self.data_source} · 开奖期：{self.issue or self.draw_date} · "
                     f"更新时间：{self.updated_at or '—'} · 状态：{'已验证' if self.verified else '未验证'}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)

    def trust_text(self) -> str:
        """兑奖信任摘要（首页/报告展示）。"""
        return (f"🎫 兑奖报告 · 开奖期 {self.issue or self.draw_date} · "
                f"号码来源 {self.data_source} · "
                f"数据更新 {self.updated_at or '—'} · 状态 {'已验证' if self.verified else '未验证'}")

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "lottery_name": self.lottery_name,
                "draw_date": self.draw_date, "matched": self.matched,
                "won": self.won, "total_winnings": round(self.total_winnings, 2),
                "unviewed": self.unviewed, "items": list(self.items),
                "disclaimer": self.disclaimer,
                "issue": self.issue, "data_source": self.data_source,
                "updated_at": self.updated_at, "verified": self.verified}


class ClaimCenter:
    """自动兑奖中心。"""

    # ---------- v4.5 P4：数据信任 ----------
    @classmethod
    def _data_source_text(cls, lottery: str) -> str:
        """号码来源：本地缓存存在则标注官方数据。"""
        try:
            from engine.data_center.providers import LocalCache
            cache = LocalCache(lottery)
            records = cache.fetch_recent(limit=1)
            return "官方数据" if records else "本地缓存"
        except Exception:
            return "官方数据"

    @classmethod
    def _data_updated_at(cls, lottery: str) -> str:
        """数据更新时间（本地缓存 meta）。"""
        try:
            from engine.data_center_v2.updater import IncrementalUpdater
            up = IncrementalUpdater(lottery)
            last = up._last_update()
            if last:
                return last[:16].replace("T", " ")
        except Exception:
            pass
        return ""

    @classmethod
    def _data_verified(cls, lottery: str, rep) -> bool:
        """校验状态：数据可读且期号匹配即已验证。"""
        if not rep or not getattr(rep, "draw_issue", ""):
            return False
        try:
            from engine.data_center.providers import LocalCache
            cache = LocalCache(lottery)
            for r in cache.fetch_recent(limit=3):
                if str(r.number) == str(rep.draw_issue):
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def _parse_date(d: str) -> Optional[date]:
        if not d:
            return None
        try:
            return date.fromisoformat(d) if len(d) == 10 else None
        except ValueError:
            return None

    @classmethod
    def _viewed_tickets(cls) -> set:
        from engine.user_events import EventTracker
        evs = EventTracker().recent("claim_viewed", limit=500)
        return {e.payload.get("ticket_id") for e in evs if e.payload.get("ticket_id")}

    @classmethod
    def status_of(cls, t: dict, today: Optional[str] = None) -> str:
        """票据 4 状态判定。"""
        today = today or date.today().isoformat()
        if t.get("claimed"):
            return "claimed"
        draw = cls._parse_date(t.get("draw_date") or "")
        if not draw or draw.isoformat() > today:
            return "waiting_draw"
        # 已开奖
        tid = t.get("ticket_id") or ""
        if tid in cls._viewed_tickets():
            return "viewed"
        return "settled_unviewed"

    @classmethod
    def build_items(cls, tickets: List[dict]) -> List[ClaimItem]:
        """构建全部票据的待兑奖列表。"""
        today = date.today().isoformat()
        items = []
        for t in tickets:
            items.append(ClaimItem(
                ticket_id=t.get("ticket_id", ""),
                lottery=t.get("lottery", "dlt"),
                front=list(t.get("front", [])),
                back=list(t.get("back", [])),
                draw_date=t.get("draw_date", ""),
                status=cls.status_of(t, today),
            ))
        return items

    @classmethod
    def pending_list(cls, tickets: List[dict]) -> List[dict]:
        """待兑奖列表（已开奖待查看 + 已查看，即待处理）。"""
        return [it.to_dict() for it in cls.build_items(tickets)
                if it.status in ("settled_unviewed", "viewed")]

    @classmethod
    def pending_text(cls, tickets: List[dict]) -> str:
        """首页/工作台展示文本。"""
        items = cls.build_items(tickets)
        waiting = sum(1 for it in items if it.status == "waiting_draw")
        unviewed = sum(1 for it in items if it.status == "settled_unviewed")
        viewed = sum(1 for it in items if it.status == "viewed")
        claimed = sum(1 for it in items if it.status == "claimed")
        lines = ["🧾 我的待兑奖"]
        lines.append(f"· 等待开奖：{waiting} 张")
        lines.append(f"· 已开奖待查看：{unviewed} 张")
        lines.append(f"· 已查看：{viewed} 张")
        lines.append(f"· 已兑奖：{claimed} 张")
        if unviewed > 0:
            lines.append("→ 开奖后自动匹配，点「刷新」查看结果")
        return "\n".join(lines)

    @classmethod
    def auto_claim(cls, tickets: List[dict], lottery: str = "dlt",
                   draw_date: Optional[str] = None,
                   notifier=None) -> AutoClaimReport:
        """自动兑奖：匹配已开奖票据 → 通知 → 生成报告（记录事件）。

        复用 v4.2 AutoReviewEngine 的归属期判定与中奖匹配。
        """
        from engine.auto_review import AutoReviewEngine
        from engine.user_events import EventTracker

        rep = AutoReviewEngine.build(tickets, lottery=lottery, draw_date=draw_date)
        report = AutoClaimReport(
            lottery=lottery,
            lottery_name=rep.lottery_name,
            draw_date=rep.draw_date,
            matched=rep.ticket_count,
            won=rep.win_tickets,
            total_winnings=rep.total_winnings,
        )
        # v4.5 P4：兑奖信任字段（开奖期/来源/更新时间/校验状态）
        report.issue = rep.draw_issue or ""
        report.data_source = cls._data_source_text(lottery)
        report.updated_at = cls._data_updated_at(lottery)
        report.verified = cls._data_verified(lottery, rep)
        # 归属本期的票据 ticket_id（与 per_ticket 顺序一致）
        part_ids = [t.get("ticket_id", "") for t in tickets
                    if AutoReviewEngine._is_this_draw(t, lottery, rep.draw_date)]
        # 待查看状态
        items = []
        for idx, it in enumerate(rep.per_ticket):
            st = "claimed" if it["won"] and False else "settled_unviewed"
            items.append({"ticket_id": part_ids[idx] if idx < len(part_ids) else "",
                          "front": it["front"], "back": it["back"],
                          "won": it["won"], "amount": it["amount"],
                          "status": st, "status_text": STATUS_TEXT[st]})
        report.items = items
        report.unviewed = rep.ticket_count - rep.win_tickets

        # 记录自动兑奖事件
        EventTracker().record("auto_claim_run", {
            "lottery": lottery, "draw_date": rep.draw_date,
            "matched": report.matched, "won": report.won,
        })

        # 通知（若提供 notifier）+ 事件
        if notifier is not None:
            ReminderEngine_local = None
            from engine.reminder_center import ReminderEngine as RE
            RE.notify_and_record(notifier, "📊 Atlas 自动兑奖", report.notify_text())
        return report

    @classmethod
    def mark_viewed(cls, ticket_id: str) -> bool:
        """标记已查看（记录事件）。"""
        from engine.user_events import EventTracker
        EventTracker().record("claim_viewed", {"ticket_id": ticket_id})
        return True

    @classmethod
    def mark_claimed(cls, ticket_id: str) -> bool:
        """标记已兑奖（TicketManager 持久化 + 事件）。"""
        from engine.ticket_system import TicketManager
        from engine.user_events import EventTracker
        mgr = TicketManager()
        if mgr.get(ticket_id) is None:
            return False
        mgr.set_claimed(ticket_id, True)
        EventTracker().record("claim_confirmed", {"ticket_id": ticket_id})
        return True
