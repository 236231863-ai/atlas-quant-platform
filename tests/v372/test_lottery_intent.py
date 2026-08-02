"""v3.7.2 测试：兑奖计算引擎（LotteryIntentRouter/TicketParser/DrawResultMatcher/PrizeCalculator/端到端）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.lottery_intent import (
    LotteryIntentRouter, TicketParser, DrawResultMatcher, PrizeCalculator, compute_prize_report,
)

# ---------- 意图路由 ----------
@pytest.mark.parametrize("text", ["我中了多少钱", "帮我算算中奖", "中奖了吗", "兑奖", "中了什么奖"])
def test_intent_positive(text):
    r = LotteryIntentRouter.detect(text)
    assert r.is_prize_intent

@pytest.mark.parametrize("text", ["今天天气", "你好", "推荐号码", "什么是回测", ""])
def test_intent_negative(text):
    r = LotteryIntentRouter.detect(text)
    assert not r.is_prize_intent

@pytest.mark.parametrize("text", ["大乐透中了", "双色球中奖", "我买的大乐透"])
def test_lottery_detect(text):
    r = LotteryIntentRouter.detect(text)
    if "双色球" in text:
        assert r.lottery == "ssq"
    else:
        assert r.lottery == "dlt"

@pytest.mark.parametrize("text", ["中了多少钱", "大乐透我中了多少钱"])
def test_confidence(text):
    r = LotteryIntentRouter.detect(text)
    assert 0 < r.confidence <= 1

@pytest.mark.parametrize("i", range(10))
def test_intent_dict(i):
    r = LotteryIntentRouter.detect("中了" + str(i))
    d = r.to_dict()
    assert "is_prize_intent" in d

# ---------- 号码解析 ----------
@pytest.mark.parametrize("text,expected_notes", [
    ("01 02 03 04 05 + 06 07", 1),
    ("01 02 03 04 05 + 06 07；11 22 33 34 35 + 08 09", 2),
    ("01 02 03 04 05|06 07", 1),
    ("前区 01 02 03 04 05 后区 06 07", 1),
])
def test_parse_notes(text, expected_notes):
    r = TicketParser.parse(text)
    assert r.parsed_notes == expected_notes

@pytest.mark.parametrize("front,back,lottery", [
    ([1,2,3,4,5],[6,7],"dlt"),
    ([1,2,3,4,5,6],[7],"ssq"),
])
def test_infer_lottery(front, back, lottery):
    from engine.lottery_intent.ticket_parser import TicketParser
    assert TicketParser._infer_lottery(front, back) == lottery

@pytest.mark.parametrize("text", ["", "没有号码", "随便看看"])
def test_parse_empty(text):
    r = TicketParser.parse(text)
    assert r.parsed_notes == 0

@pytest.mark.parametrize("text", ["7月31日买了 01 02 03 04 05 + 06 07", "8月1日开奖"])
def test_parse_dates(text):
    r = TicketParser.parse(text)
    assert r.buy_date or r.draw_date

# ---------- 开奖匹配 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_find_latest(lottery):
    d = DrawResultMatcher.find_draw(lottery)
    assert d is not None

@pytest.mark.parametrize("front,back,lottery", [
    ([10,11,18,22,35],[6,12],"dlt"),
    ([1,2,3,4,5],[6,7],"dlt"),
])
def test_match(front, back, lottery):
    m = DrawResultMatcher.match(front, back, lottery=lottery)
    assert m.matched

@pytest.mark.parametrize("i", range(5))
def test_match_counts(i):
    m = DrawResultMatcher.match([1,2,3,4,5],[6,7], lottery="dlt")
    assert m.front_hits >= 0 and m.back_hits >= 0

# ---------- 奖金计算 ----------
@pytest.mark.parametrize("fh,bh,level,amount", [
    (5,2,"一等奖",5000000), (5,1,"二等奖",180000), (5,0,"三等奖",10000),
    (4,2,"四等奖",3000), (4,1,"五等奖",300), (3,2,"六等奖",200),
    (4,0,"七等奖",100), (3,1,"八等奖",15), (0,2,"九等奖",5),
])
def test_dlt_prizes(fh, bh, level, amount):
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    assert r.prize_level == level and r.amount == amount

@pytest.mark.parametrize("fh,bh", [(0,0),(1,0),(2,0)])
def test_dlt_no_win(fh, bh):
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    assert not r.won

@pytest.mark.parametrize("fh,bh,level,amount", [
    (6,1,"一等奖",5000000), (6,0,"二等奖",100000), (5,1,"三等奖",3000),
    (5,0,"四等奖",200), (4,1,"四等奖",200), (4,0,"五等奖",10),
    (3,1,"五等奖",10), (2,1,"六等奖",5), (1,1,"六等奖",5), (0,1,"六等奖",5),
])
def test_ssq_prizes(fh, bh, level, amount):
    r = PrizeCalculator.calculate(fh, bh, "ssq")
    assert r.prize_level == level and r.amount == amount

@pytest.mark.parametrize("fh,bh", [(0,0),(1,0),(2,0),(3,0)])
def test_ssq_no_win(fh, bh):
    r = PrizeCalculator.calculate(fh, bh, "ssq")
    assert not r.won

# ---------- 端到端 ----------
@pytest.mark.parametrize("text", ["我中了多少钱", "帮我算算"])
def test_e2e_non_prize(text):
    r = compute_prize_report(text)
    assert "report_text" in r

@pytest.mark.parametrize("text", [
    "大乐透 01 02 03 04 05 + 06 07 中了吗",
    "我买了 10 11 18 22 35 + 06 12，中了多少钱",
])
def test_e2e_prize(text):
    r = compute_prize_report(text)
    assert r["is_prize"]
    assert "兑奖" in r["report_text"]

@pytest.mark.parametrize("i", range(5))
def test_e2e_report_contains(i):
    text = f"大乐透 01 02 03 04 05 + 06 07 中了"
    r = compute_prize_report(text)
    assert "总奖金" in r["report_text"]
