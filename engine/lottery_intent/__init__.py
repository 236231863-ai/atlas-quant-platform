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
    """端到端：用户输入 → 奖金报告。

    返回 dict（含 intent / tickets / matches / report_text）。
    """
    intent = LotteryIntentRouter.detect(user_input)
    if not intent.is_prize_intent:
        return {"intent": intent.to_dict(), "is_prize": False, "report_text": "未识别到兑奖意图。"}

    parse = TicketParser.parse(user_input)
    lottery = intent.lottery or parse.lottery or "dlt"
    if not parse.is_viable:
        return {"intent": intent.to_dict(), "is_prize": True, "tickets": 0, "report_text": "未解析到有效号码，请按「前区+后区」格式提供。"}

    matcher = DrawResultMatcher()
    matches = []
    for t in parse.tickets:
        m = matcher.match(t.front, t.back, lottery=lottery, date=parse.draw_date or parse.buy_date)
        matches.append(m)

    summary = PrizeCalculator.total_for(matches, lottery)
    draw = matches[0].draw if matches and matches[0].draw else None

    lines = ["🎯 兑奖计算结果"]
    lines.append(f"· 识别彩种：{'大乐透' if lottery == 'dlt' else '双色球'}")
    lines.append(f"· 解析注数：{parse.parsed_notes} 注")
    if draw:
        lines.append(f"· 开奖：{draw.number}（{draw.draw_date}）{draw.format_front()} + {draw.format_back()}")
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
        "draw": {"issue": draw.number, "date": draw.draw_date} if draw else {},
        "report_text": "\n".join(lines),
    }


__all__ = [
    "LotteryIntentRouter", "IntentResult", "TicketParser", "Ticket", "TicketParseResult",
    "DrawResultMatcher", "DrawMatch", "PrizeCalculator", "PrizeResult", "compute_prize_report",
]
