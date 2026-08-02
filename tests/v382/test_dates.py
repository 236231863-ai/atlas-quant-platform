"""v3.8.0 日期升级测试：日期意图 / 开奖匹配 / 防错确认 / 防穿越。"""
import pytest
from engine.ticket_system.date_parser import DateIntentParser
from engine.ticket_system.schedule import LotterySchedule
from engine.lottery_intent import compute_prize_report, DrawResultMatcher
from engine.assistant import AssistantIntentRouter

def P(t): return DateIntentParser.parse(t)

# ---------- 日期意图解析 ----------
@pytest.mark.parametrize("text,exp_buy,exp_draw", [
    ("7月31日买的", "2026-07-31", None),
    ("7月31日买的，8月1日开奖", "2026-07-31", "2026-08-01"),
    ("8月1日开奖", None, "2026-08-01"),
    ("2026年7月31日购买", "2026-07-31", None),
])
def test_date_intent_scenarios(text, exp_buy, exp_draw):
    r = P(text)
    assert r.purchase_date == exp_buy
    assert r.draw_date == exp_draw

@pytest.mark.parametrize("text", ["昨天买的", "前天买的", "今天买的"])
def test_relative_dates(text):
    from datetime import date, timedelta
    r = P(text)
    assert r.purchase_date is not None
    today = date.today()
    exp = {"昨天买的": (today - timedelta(days=1)).isoformat(),
           "前天买的": (today - timedelta(days=2)).isoformat(),
           "今天买的": today.isoformat()}[text]
    assert r.purchase_date == exp

@pytest.mark.parametrize("text,need", [("7月31日买的", True), ("7月31日买的，8月1日开奖", False), ("8月1日开奖", False)])
def test_need_confirm(text, need):
    assert P(text).need_confirm == need

# ---------- 开奖日程 ----------
@pytest.mark.parametrize("lottery,from_d,expected", [
    ("dlt", "2026-07-31", "2026-08-01"),  # 周五 → 周六
    ("dlt", "2026-08-01", "2026-08-01"),  # 周六即开奖日
    ("ssq", "2026-07-31", "2026-08-02"),  # 周五 → 周日
])
def test_next_draw_date(lottery, from_d, expected):
    assert LotterySchedule.next_draw_date(lottery, from_d) == expected

@pytest.mark.parametrize("lottery,date_str,expected", [
    ("dlt", "2026-08-01", True), ("dlt", "2026-08-02", False), ("ssq", "2026-08-02", True),
])
def test_is_draw_day(lottery, date_str, expected):
    assert LotterySchedule.is_draw_day(lottery, date_str) == expected

# ---------- 防穿越历史 ----------
def test_no_historical_match():
    """2026-07-31 购买 → 匹配 2026-08-01 开奖（非 2024）"""
    r = compute_prize_report("2026年7月31日买了 10 11 18 22 35 + 06 12，8月1日开奖")
    assert r.get("draw", {}).get("date") == "2026-08-01"

def test_exact_date_match():
    d = DrawResultMatcher.find_draw("dlt", date="2026-08-01")
    assert d is not None and d.draw_date == "2026-08-01"

# ---------- 防错确认 ----------
def test_confirm_only_purchase():
    r = compute_prize_report("7月31日买了 10 11 18 22 35 + 06 12")
    assert r.get("need_confirm") is True
    assert "是否按" in r["report_text"]

@pytest.mark.parametrize("text", ["7月31日买 01 02 03 04 05 + 06 07", "昨天买 05 10 15 20 25 + 08 09"])
def test_confirm_variants(text):
    r = compute_prize_report(text)
    assert r.get("need_confirm") is True or r.get("tickets", 0) > 0

# ---------- 兑奖工具路由 ----------
def test_route_prize_no_numbers():
    router = AssistantIntentRouter()
    r = router.route("8月1日开奖，我中了多少钱")
    assert r.is_business and r.tool == "prize"

def test_no_numbers_guide():
    r = compute_prize_report("8月1日开奖，我中了多少钱")
    assert "号码" in r["report_text"]

# ---------- 投注信息 UI ----------
def test_report_investment_info():
    r = compute_prize_report("7月31日买 10 11 18 22 35 + 06 12，8月1日开奖")
    text = r["report_text"]
    assert "购买日期" in text and "开奖日期" in text
    assert "匹配状态" in text

@pytest.mark.parametrize("i", range(10))
def test_report_deterministic(i):
    a = compute_prize_report("7月31日买 10 11 18 22 35 + 06 12，8月1日开奖")
    b = compute_prize_report("7月31日买 10 11 18 22 35 + 06 12，8月1日开奖")
    assert a["draw"] == b["draw"]

# ---------- 端到端 15 注 ----------
def test_e2e_15_notes():
    notes = "; ".join(f"0{i%9+1} 0{i%8+2} 0{i%7+3} 0{i%6+4} 0{i%5+5} + 0{i%4+6} 0{i%3+7}" for i in range(15))
    text = f"7月31日买了 {notes}，8月1日开奖，我中了多少奖金？"
    r = compute_prize_report(text)
    assert r.get("tickets") == 15
    assert r.get("draw", {}).get("issue") == "26086"

@pytest.mark.parametrize("i", range(5))
def test_e2e_repeat(i):
    test_e2e_15_notes()
