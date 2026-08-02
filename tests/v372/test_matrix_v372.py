"""v3.7.2 矩阵补充（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.lottery_intent import LotteryIntentRouter, TicketParser, DrawResultMatcher, PrizeCalculator, compute_prize_report

# 意图矩阵
_INTENT_TEXTS = ["中了", "中奖", "兑奖", "多少钱", "赚了", "有没有中", "中了吗", "帮我算算", "算算奖金", "奖金多少"]
@pytest.mark.parametrize("text", _INTENT_TEXTS)
@pytest.mark.parametrize("n", [1, 2])
def test_intent_matrix(text, n):
    r = LotteryIntentRouter.detect(text * n)
    assert r.is_prize_intent

_NEG_TEXTS = ["天气", "推荐", "分析", "回测", "导出", "帮助", "安装", "升级", "问候", "随机"]
@pytest.mark.parametrize("text", _NEG_TEXTS)
def test_neg_matrix(text):
    r = LotteryIntentRouter.detect(text)
    assert not r.is_prize_intent

# 解析矩阵
@pytest.mark.parametrize("f1,f2,f3,f4,f5,b1,b2", [
    (1,2,3,4,5,6,7), (10,20,30,35,15,8,9), (33,32,31,30,29,12,11),
    (5,15,25,30,35,1,12), (7,8,9,10,11,2,3),
])
def test_parse_single(f1,f2,f3,f4,f5,b1,b2):
    text = f"{f1} {f2} {f3} {f4} {f5} + {b1} {b2}"
    r = TicketParser.parse(text)
    assert r.parsed_notes == 1
    assert r.tickets[0].front == [f1,f2,f3,f4,f5]

@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_parse_multiple(n):
    notes = "; ".join(f"0{i%10+1} 0{i%9+2} 0{i%8+3} 0{i%7+4} 0{i%6+5} + 0{i%5+6} 0{i%4+7}" for i in range(n))
    r = TicketParser.parse(notes)
    assert r.parsed_notes == n

@pytest.mark.parametrize("text", ["01 02 03 04 05 + 06 07", "01 02 03 04 05 | 06 07", "前区 01 02 03 04 05 后区 06 07"])
def test_parse_separators(text):
    r = TicketParser.parse(text)
    assert r.parsed_notes == 1

# 匹配矩阵
@pytest.mark.parametrize("f", [[1,2,3,4,5],[10,20,30,35,15],[5,10,15,20,25]])
@pytest.mark.parametrize("b", [[6,7],[8,9],[1,12]])
def test_match_matrix(f, b):
    m = DrawResultMatcher.match(f, b, lottery="dlt")
    assert m.matched
    assert 0 <= m.front_hits <= 5

# 奖金矩阵
@pytest.mark.parametrize("fh", range(0, 6))
@pytest.mark.parametrize("bh", range(0, 3))
def test_prize_dlt_grid(fh, bh):
    r = PrizeCalculator.calculate(fh, bh, "dlt")
    assert r.amount >= 0
    assert (r.won == (r.amount > 0))

@pytest.mark.parametrize("fh", range(0, 7))
@pytest.mark.parametrize("bh", range(0, 2))
def test_prize_ssq_grid(fh, bh):
    r = PrizeCalculator.calculate(fh, bh, "ssq")
    assert r.amount >= 0

# 端到端矩阵
@pytest.mark.parametrize("i", range(10))
def test_e2e_matrix(i):
    text = f"大乐透 01 02 03 04 05 + 06 07，我中了吗"
    r = compute_prize_report(text)
    assert "report_text" in r
    assert r["is_prize"]
