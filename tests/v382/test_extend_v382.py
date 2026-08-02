"""v3.8.0 日期升级补充矩阵。"""
import pytest
from engine.ticket_system.date_parser import DateIntentParser
from engine.ticket_system.schedule import LotterySchedule
from engine.lottery_intent import compute_prize_report, DrawResultMatcher

def P(t): return DateIntentParser.parse(t)

# 日期解析扩展
@pytest.mark.parametrize("text", [
    "1月1日买", "12月31日买", "2月28日购买", "3月15日购彩", "6月30日买彩票",
])
def test_date_month_day(text):
    r = P(text)
    assert r.purchase_date is not None
    assert len(r.purchase_date) == 10

@pytest.mark.parametrize("text", [
    "2026-01-15买", "2025-12-01购买", "2024-06-30买",
])
def test_abs_dates(text):
    r = P(text)
    assert r.purchase_date is not None

# 开奖日程扩展
@pytest.mark.parametrize("dow,d_from,d_exp", [
    ("dlt", "2026-08-02", "2026-08-03"),  # 周日→周一
    ("dlt", "2026-08-04", "2026-08-05"),  # 周二→周三
    ("ssq", "2026-08-01", "2026-08-02"),
    ("ssq", "2026-08-03", "2026-08-04"),
])
def test_schedule_week(dow, d_from, d_exp):
    assert LotterySchedule.next_draw_date(dow, d_from) == d_exp

# 精确匹配防穿越
@pytest.mark.parametrize("date_str", ["2026-08-01", "2026-07-30", "2026-07-29"])
def test_exact_match_multi(date_str):
    d = DrawResultMatcher.find_draw("dlt", date=date_str)
    if d:
        assert d.draw_date == date_str

# 确认文案
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_confirm_lottery(lottery):
    text = f"{'大乐透' if lottery=='dlt' else '双色球'} 01 02 03 04 05 + 06 07 昨天买的"
    r = compute_prize_report(text)
    assert r.get("need_confirm") is True or "是否按" in r.get("report_text", "")

# 端到端多注
@pytest.mark.parametrize("n", [1, 5, 10, 15])
def test_e2e_n_notes(n):
    notes = "; ".join(f"{i%9+1} {i%8+2} {i%7+3} {i%6+4} {i%5+5} + {i%4+6} {i%3+7}" for i in range(n))
    r = compute_prize_report(f"7月31日买 {notes}，8月1日开奖")
    assert r.get("tickets") == n

@pytest.mark.parametrize("i", range(10))
def test_route_stable(i):
    from engine.assistant import AssistantIntentRouter
    r = AssistantIntentRouter().route("7月31日买 01 02 03 04 05 + 06 07 中了")
    assert r.is_business
