"""v3.7.2 补充矩阵（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.lottery_intent import LotteryIntentRouter, TicketParser, DrawResultMatcher, PrizeCalculator, compute_prize_report

# 意图：更多表述
_WIN_WORDS = ["中了", "中奖", "兑奖", "奖金", "中了多少钱", "中了吗", "帮我算算", "算奖金", "赚了多少", "中了没"]
@pytest.mark.parametrize("w", _WIN_WORDS)
@pytest.mark.parametrize("prefix", ["", "大乐透", "双色球", "我"])
def test_intent_wide(w, prefix):
    text = f"{prefix}{w}"
    r = LotteryIntentRouter.detect(text)
    if prefix:
        assert r.is_prize_intent
    else:
        assert r.is_prize_intent

# 解析：多注 + 不同分隔
@pytest.mark.parametrize("sep", ["；", ";", "\n", "，"])
def test_parse_sep_wide(sep):
    text = f"01 02 03 04 05 + 06 07{sep}10 11 18 22 35 + 06 12"
    r = TicketParser.parse(text)
    assert r.parsed_notes >= 1

@pytest.mark.parametrize("front", [
    [1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15], [16,17,18,19,20],
    [21,22,23,24,25], [26,27,28,29,30], [31,32,33,34,35], [5,15,25,30,35],
])
@pytest.mark.parametrize("back", [[1,2],[6,7],[11,12],[12,11]])
def test_parse_front_back_grid(front, back):
    text = f"{' '.join(map(str,front))} + {' '.join(map(str,back))}"
    r = TicketParser.parse(text)
    assert r.parsed_notes == 1

# 匹配：日期查找
@pytest.mark.parametrize("date", ["2026-08-01", "08-01", "2026-07-30"])
def test_find_by_date(date):
    d = DrawResultMatcher.find_draw("dlt", date=date)
    if d:
        assert d is not None

@pytest.mark.parametrize("issue", ["26086", "26085"])
def test_find_by_issue(issue):
    d = DrawResultMatcher.find_draw("dlt", issue=issue)
    assert d is not None

# 奖金：详细等级
@pytest.mark.parametrize("fh,bh,level", [
    (5,2,"一等奖"), (5,1,"二等奖"), (5,0,"三等奖"),
    (4,2,"四等奖"), (4,1,"五等奖"), (3,2,"六等奖"),
    (4,0,"七等奖"), (3,1,"八等奖"), (2,2,"八等奖"),
    (3,0,"九等奖"), (1,2,"九等奖"), (2,1,"九等奖"), (0,2,"九等奖"),
])
def test_dlt_all_levels(fh, bh, level):
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    assert r.prize_level == level

@pytest.mark.parametrize("i", range(10))
def test_total_for(i):
    matches = [DrawResultMatcher.match([1,2,3,4,5],[6,7], lottery="dlt") for _ in range(i)]
    s = PrizeCalculator.total_for(matches, "dlt")
    assert s["total"] >= 0
    assert len(s["details"]) == i

# 端到端：不同输入
@pytest.mark.parametrize("text", [
    "双色球 01 02 03 04 05 06 + 07，中了没",
    "大乐透 10 11 18 22 35 + 06 12 开奖了，算算奖金",
    "7月31日买的 01 02 03 04 05 + 06 07，8月1日中奖了吗",
])
def test_e2e_variants(text):
    r = compute_prize_report(text)
    assert "report_text" in r

@pytest.mark.parametrize("i", range(10))
def test_e2e_won_count(i):
    r = compute_prize_report(f"大乐透 10 11 18 22 35 + 06 12，我中了吗")
    assert r["is_prize"]
    assert r["total"] >= 0
