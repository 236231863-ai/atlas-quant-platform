"""lottery_intent - 用户任务理解（v3.7.2）。

兑奖计算全链路：
  LotteryIntentRouter → 意图+彩种识别
  TicketParser        → 号码/注数/日期解析
  DrawResultMatcher   → 开奖匹配
  PrizeCalculator     → 奖金计算
"""
from .intent_router import LotteryIntentRouter, IntentResult
from .ticket_parser import TicketParser, Ticket, TicketParseResult
from .draw_matcher import DrawResultMatcher, DrawMatch
from .prize_calculator import PrizeCalculator, PrizeResult


def compute_prize_report(user_input: str) -> dict:
    """端到端：用户输入 → 奖金报告（v3.8.0 日期升级）。

    流程：
      1. 意图识别
      2. 日期意图解析（购买日/开奖日，支持相对日期）
      3. 仅购买日 → 防错确认（询问是否按下一开奖计算）
      4. LotterySchedule 推算开奖日 → 精确匹配期号（防穿越）
      5. 计算奖金 → 投注信息 + 结果报告
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

    # Phase 3：防错确认——仅购买日期无开奖日期
    if date_intent.has_purchase and not date_intent.has_draw and parse.is_viable:
        next_draw = LotterySchedule.next_draw_date(lottery, date_intent.purchase_date)
        confirm = (
            f"我识别到：\n购买日期：{date_intent.purchase_date}\n"
            f"{LotterySchedule.lottery_name(lottery)}下一开奖：{next_draw}\n"
            f"是否按 {next_draw} 开奖计算？"
        )
        return {
            "intent": intent.to_dict(), "is_prize": True, "need_confirm": True,
            "lottery": lottery, "tickets": parse.parsed_notes,
            "purchase_date": date_intent.purchase_date,
            "next_draw": next_draw,
            "report_text": confirm,
        }

    if not parse.is_viable:
        return {"intent": intent.to_dict(), "is_prize": True, "tickets": 0, "report_text": "未解析到有效号码，请按「前区+后区」格式提供。"}

    # Phase 2：按购买日/开奖日匹配（LotterySchedule 推算）
    matcher = DrawResultMatcher()
    resolved_draw_date = matcher.resolve_draw_date(
        lottery, purchase_date=date_intent.purchase_date, draw_date=date_intent.draw_date)
    matches = []
    for t in parse.tickets:
        m = matcher.match(t.front, t.back, lottery=lottery,
                          purchase_date=date_intent.purchase_date, draw_date=date_intent.draw_date)
        matches.append(m)

    summary = PrizeCalculator.total_for(matches, lottery)
    draw = matches[0].draw if matches and matches[0].draw else None

    # Phase 5：投注信息 + 结果
    lines = ["🎫 投注信息"]
    lines.append(f"· 购买日期：{date_intent.purchase_date or '未知'}")
    lines.append(f"· 开奖日期：{resolved_draw_date or '未知'}")
    lines.append(f"· 开奖期号：{draw.number if draw else '未找到'}")
    lines.append(f"· 匹配状态：{'已兑奖' if draw else '未匹配到开奖'}")
    lines.append("")
    lines.append("🎯 兑奖计算结果")
    lines.append(f"· 识别彩种：{LotterySchedule.lottery_name(lottery)}")
    lines.append(f"· 解析注数：{parse.parsed_notes} 注")
    if draw:
        lines.append(f"· 开奖号码：{draw.format_front()} + {draw.format_back()}")
    lines.append(f"· 中奖注数：{summary['won_notes']} / {parse.parsed_notes}")
    lines.append(f"· 💰 总奖金：¥{summary['total']:,.0f}")
    for i, d in enumerate(summary["details"][:8], 1):
        if d["level"]:
            lines.append(f"  第{i}注：中{d['front_hit']}+{d['back_hit']} → {d['level']} ¥{d['amount']:,.0f}")
    if summary["won_notes"] == 0:
        lines.append("· 很遗憾，本次未中奖。")
    lines.append("· 本结果基于官方开奖数据，仅供参考。")
    return {
        "intent": intent.to_dict(),
        "is_prize": True,
        "lottery": lottery,
        "tickets": parse.parsed_notes,
        "won_notes": summary["won_notes"],
        "total": summary["total"],
        "purchase_date": date_intent.purchase_date,
        "draw_date": resolved_draw_date,
        "draw": {"issue": draw.number, "date": draw.draw_date} if draw else {},
        "report_text": "\n".join(lines),
    }


__all__ = [
    "LotteryIntentRouter", "IntentResult", "TicketParser", "Ticket", "TicketParseResult",
    "DrawResultMatcher", "DrawMatch", "PrizeCalculator", "PrizeResult", "compute_prize_report",
]
