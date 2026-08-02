"""lottery_intent - 用户任务理解（v3.8.2-P1 确认恢复）。

兑奖计算全链路：
  LotteryIntentRouter → 意图+彩种识别
  TicketParser        → 号码/注数/日期解析（含连续号码串）
  DrawResultMatcher   → 开奖匹配
  PrizeCalculator     → 奖金计算
  PendingTaskManager  → 确认回复恢复任务（v3.8.2-P1 Phase 1/4）

核心修复（v3.8.2-P1）：
  用户问兑奖 → Atlas 返回确认 → 用户回复"是的"
  → 自动恢复 PendingTask 并完成兑奖（不再进入普通聊天）。
"""
from .intent_router import LotteryIntentRouter, IntentResult
from .ticket_parser import TicketParser, Ticket, TicketParseResult
from .draw_matcher import DrawResultMatcher, DrawMatch
from .prize_calculator import PrizeCalculator, PrizeResult


def _draw_record_text(draw, lottery: str) -> str:
    from engine.ticket_system.schedule import LotterySchedule
    return f"{LotterySchedule.lottery_name(lottery)} 第 {draw.number} 期（{draw.draw_date}）：{draw.format_front()} + {draw.format_back()}"


def _build_prize_result(lottery: str, tickets: list,
                        purchase_date: str = "", draw_date: str = "") -> dict:
    """用已解析票据计算奖金并生成报告（v3.8.2-P1 Phase 5 增强）。

    tickets: [Ticket] 或 [{"front":[...], "back":[...]}]
    """
    matcher = DrawResultMatcher()
    matches = []
    for t in tickets:
        if isinstance(t, Ticket):
            front, back = t.front, t.back
        else:
            front, back = t.get("front", []), t.get("back", [])
        m = matcher.match(front, back, lottery=lottery,
                          purchase_date=purchase_date, draw_date=draw_date)
        matches.append(m)

    summary = PrizeCalculator.total_for(matches, lottery)
    draw = matches[0].draw if matches and matches[0].draw else None
    resolved_draw_date = matcher.resolve_draw_date(
        lottery, purchase_date=purchase_date, draw_date=draw_date)
    note_count = len(tickets)

    # 每注明细补充号码文本（Phase 3 逐注验证 + Phase 5 展示）
    details = []
    for i, m in enumerate(matches):
        raw = summary["details"][i] if i < len(summary["details"]) else {}
        t = tickets[i]
        front = t.front if isinstance(t, Ticket) else t.get("front", [])
        back = t.back if isinstance(t, Ticket) else t.get("back", [])
        details.append({
            **raw,
            "front": list(front), "back": list(back),
            "front_text": " ".join(f"{n:02d}" for n in front),
            "back_text": " ".join(f"{n:02d}" for n in back),
            "hit_text": f"中{raw.get('front_hit', 0)}+{raw.get('back_hit', 0)}",
        })

    # Phase 5 报告增强：购买/开奖/期号/注数/中奖注数/等级/总奖金
    lines = ["🎫 投注信息"]
    lines.append(f"· 购买日期：{purchase_date or '未提供（输入日期可精确匹配）'}")
    lines.append(f"· 开奖日期：{resolved_draw_date or '未找到开奖'}")
    lines.append(f"· 开奖期号：{draw.number if draw else '未找到'}")
    lines.append(f"· 投注注数：{note_count} 注")
    lines.append(f"· 匹配状态：{'已兑奖' if draw else '未匹配到开奖'}")
    lines.append("")
    lines.append("🎯 兑奖计算结果")
    from engine.ticket_system.schedule import LotterySchedule
    lines.append(f"· 识别彩种：{LotterySchedule.lottery_name(lottery)}")
    if draw:
        lines.append(f"· 开奖号码：{draw.format_front()} + {draw.format_back()}")
    lines.append(f"· 中奖注数：{summary['won_notes']} / {note_count}")
    lines.append(f"· 💰 总奖金：¥{summary['total']:,.0f}")

    # 每注明细（号码 + 匹配情况 + 等级 + 奖金）
    max_detail = 20
    show_all = note_count <= max_detail
    shown = 0
    for i, d in enumerate(details, 1):
        if d["level"]:
            shown += 1
            lines.append(f"  第{i}注：{d['front_text']} + {d['back_text']} "
                         f"→ {d['hit_text']} {d['level']} ¥{d['amount']:,.0f}")
        elif show_all:
            lines.append(f"  第{i}注：{d['front_text']} + {d['back_text']} → 未中奖")
    if not show_all:
        lines.append(f"  （仅列出中奖注 {shown} 条，共 {note_count} 注）")
    if summary["won_notes"] == 0:
        lines.append("· 很遗憾，本次未中奖。")
    lines.append("· 本结果基于官方开奖数据，仅供参考。")

    return {
        "is_prize": True,
        "lottery": lottery,
        "tickets": note_count,
        "won_notes": summary["won_notes"],
        "total": summary["total"],
        "purchase_date": purchase_date,
        "draw_date": resolved_draw_date,
        "draw": {"issue": draw.number, "date": draw.draw_date} if draw else {},
        "note_details": details,
        "report_text": "\n".join(lines),
    }


def compute_prize_report(user_input: str, user_id: str = "default") -> dict:
    """端到端：用户输入 → 奖金报告（v3.8.2-P1 确认恢复）。

    流程：
      1. 意图识别
      2. 日期意图解析（购买日/开奖日，支持相对日期）
      3. 仅购买日 → 创建 PendingTask + 防错确认
      4. LotterySchedule 推算开奖日 → 精确匹配期号（防穿越）
      5. 计算奖金 → 投注信息 + 结果报告（Phase 5 增强）
    """
    intent = LotteryIntentRouter.detect(user_input)
    if not intent.is_prize_intent:
        return {"intent": intent.to_dict(), "is_prize": False, "report_text": "未识别到兑奖意图。"}

    parse = TicketParser.parse(user_input)
    lottery = intent.lottery or parse.lottery or "dlt"

    # Phase 1：日期意图解析
    from engine.ticket_system.date_parser import DateIntentParser
    from engine.ticket_system.schedule import LotterySchedule
    date_intent = DateIntentParser.parse(user_input)

    # Phase 3 + Phase 1：仅购买日期 → 保存 PendingTask + 防错确认
    if date_intent.has_purchase and not date_intent.has_draw and parse.is_viable:
        next_draw = LotterySchedule.next_draw_date(lottery, date_intent.purchase_date)
        # 保存待确认任务（Phase 1 PendingTaskManager）
        from engine.task_context import PendingTaskManager
        mgr = PendingTaskManager()
        mgr.create_task(
            user_id, task_type="prize", lottery_type=lottery,
            tickets=parse.to_ticket_dicts(),
            purchase_date=date_intent.purchase_date,
            draw_date=next_draw or "",
        )
        confirm = (
            f"我识别到：\n购买日期：{date_intent.purchase_date}\n"
            f"识别注数：{parse.parsed_notes} 注\n"
            f"{LotterySchedule.lottery_name(lottery)}下一开奖：{next_draw}\n"
            f"是否按 {next_draw} 开奖计算？\n"
            f"（回复「是 / 好的 / 确认」即可自动计算）"
        )
        return {
            "intent": intent.to_dict(), "is_prize": True, "need_confirm": True,
            "lottery": lottery, "tickets": parse.parsed_notes,
            "purchase_date": date_intent.purchase_date,
            "next_draw": next_draw,
            "report_text": confirm,
        }

    if not parse.is_viable:
        return {"intent": intent.to_dict(), "is_prize": True, "tickets": 0,
                "report_text": "未解析到有效号码，请按「前区+后区」格式或连续号码串提供。"}

    # Phase 2：按购买日/开奖日匹配 + 计算
    result = _build_prize_result(
        lottery, parse.tickets,
        purchase_date=date_intent.purchase_date, draw_date=date_intent.draw_date)
    result["intent"] = intent.to_dict()
    return result


def confirm_prize_task(user_id: str = "default") -> dict:
    """用户确认后，恢复 PendingTask 并完成兑奖（v3.8.2-P1 Phase 4）。

    从 PendingTaskManager 取出保存的票据/日期 → 计算 → 返回完整报告。
    """
    from engine.task_context import PendingTaskManager
    mgr = PendingTaskManager()
    task = mgr.confirm_task(user_id)
    if task is None:
        return {"confirmed": False, "is_prize": False,
                "report_text": "当前没有待确认的兑奖任务。"}

    result = _build_prize_result(
        task.lottery_type, task.tickets,
        purchase_date=task.purchase_date, draw_date=task.draw_date)
    result["confirmed"] = True
    result["resumed_from_task"] = True
    return result


def cancel_prize_task(user_id: str = "default") -> dict:
    """用户否定确认时清除任务。"""
    from engine.task_context import PendingTaskManager
    mgr = PendingTaskManager()
    cleared = mgr.clear_task(user_id)
    return {"cleared": cleared,
            "report_text": "已取消本次兑奖计算。你可以重新输入号码。" if cleared else "当前没有待确认的任务。"}


__all__ = [
    "LotteryIntentRouter", "IntentResult", "TicketParser", "Ticket", "TicketParseResult",
    "DrawResultMatcher", "DrawMatch", "PrizeCalculator", "PrizeResult",
    "compute_prize_report", "confirm_prize_task", "cancel_prize_task",
]
