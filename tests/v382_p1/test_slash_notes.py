"""v4.0.1 修复：'/' 分隔多注 + '+' 前后区格式兑奖解析回归测试。"""
from __future__ import annotations

import pytest

from engine.lottery_intent.ticket_parser import TicketParser
from engine.lottery_intent import compute_prize_report
from engine.assistant import handle_query

# 用户真实输入：/ 分隔 15 注 + 前后区
SLASH_15 = (
    "13 21 23 26 33+ 01 12 / 05 19 23 32 34+ 02 11 / 03 18 24 30 33+ 05 12 / "
    "06 14 26 31 35+ 01 06 / 09 17 21 28 34+ 03 10 / 09 13 23 26 32+ 11 12 / "
    "02 12 13 23 26+ 02 05 / 02 09 13 21 26+ 02 11 / 03 09 16 23 26+ 08 12 / "
    "09 13 23 26 32+ 01 12 / 03 10 13 23 26+ 05 11 / 02 12 19 26 33+ 02 08 / "
    "06 16 21 30 34+ 06 12 / 03 09 18 27 35+ 01 07 / 08 18 24 31 35+ 04 09"
)


def test_slash_notes_15():
    r = TicketParser.parse(SLASH_15)
    assert r.parsed_notes == 15
    assert r.lottery == "dlt"


def test_slash_notes_first_note():
    r = TicketParser.parse(SLASH_15)
    assert r.tickets[0].front == [13, 21, 23, 26, 33]
    assert r.tickets[0].back == [1, 12]


def test_slash_notes_last_note():
    r = TicketParser.parse(SLASH_15)
    assert r.tickets[14].front == [8, 18, 24, 31, 35]
    assert r.tickets[14].back == [4, 9]


@pytest.mark.parametrize("i", range(15))
def test_slash_notes_each_valid(i):
    r = TicketParser.parse(SLASH_15)
    t = r.tickets[i]
    assert len(t.front) == 5
    assert len(t.back) == 2
    assert all(1 <= n <= 35 for n in t.front)
    assert all(1 <= n <= 12 for n in t.back)


def test_slash_no_plus():
    """/ 分隔但无 +（每注 7 个数字）。"""
    s = "01 02 03 04 05 06 07 / 08 09 10 11 12 13 14"
    r = TicketParser.parse(s)
    assert r.parsed_notes == 2


def test_slash_mixed_spaces():
    """/ 分隔 + 前区后区关键词混合。"""
    s = "前区 13 21 23 26 33 后区 01 12 / 05 19 23 32 34+ 02 11"
    r = TicketParser.parse(s)
    assert r.parsed_notes == 2


def test_slash_with_date():
    r = TicketParser.parse(f"7月31日买的：{SLASH_15}")
    assert r.parsed_notes == 15
    assert r.buy_date == "07-31"


def test_slash_semicolon_mix():
    """/ 与分号混用。"""
    s = "01 02 03 04 05 + 06 07；08 09 10 11 12 + 13 14 / 15 16 17 18 19 + 01 02"
    r = TicketParser.parse(s)
    assert r.parsed_notes == 3


def test_prize_report_recognizes_15():
    """兑奖链路识别 15 注（不再返回"请提供号码"）。"""
    r = compute_prize_report(f"7月31日买了这15组，能得多少奖金：{SLASH_15}")
    assert r.get("tickets") == 15
    assert r.get("need_confirm") is True
    assert "15 注" in r["report_text"]


def test_handle_query_slash_flow(task_storage):
    """AI 助手完整流程：识别 15 注 → 确认 → 兑奖。"""
    q = f"7月31日我购买了这些号码，想知道能获得多少奖金：{SLASH_15}"
    r1 = handle_query(q)
    assert "是否按" in r1
    assert "15 注" in r1
    r2 = handle_query("是的")
    assert "总奖金" in r2
    assert "投注注数：15 注" in r2
    assert "26086" in r2


def test_handle_query_no_banned(task_storage):
    """不再返回"请提供号码"或误判为统计。"""
    q = f"7月31日买了这些号码：{SLASH_15}"
    r1 = handle_query(q)
    assert "请提供你的号码" not in r1
    assert "历史开奖" not in r1


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("n", [2, 3, 5, 8])
def test_slash_various_counts(n):
    import random
    rng = random.Random(n)
    notes = []
    for _ in range(n):
        f = sorted(rng.sample(range(1, 36), 5))
        b = sorted(rng.sample(range(1, 13), 2))
        notes.append(" ".join(f"{x:02d}" for x in f) + "+ " + " ".join(f"{x:02d}" for x in b))
    s = " / ".join(notes)
    r = TicketParser.parse(s)
    assert r.parsed_notes == n


@pytest.mark.parametrize("seed", range(20))
def test_slash_random_valid(seed):
    import random
    rng = random.Random(seed)
    n = rng.randint(2, 10)
    notes = []
    for _ in range(n):
        f = sorted(rng.sample(range(1, 36), 5))
        b = sorted(rng.sample(range(1, 13), 2))
        notes.append(" ".join(f"{x:02d}" for x in f) + "+ " + " ".join(f"{x:02d}" for x in b))
    s = " / ".join(notes)
    r = TicketParser.parse(s)
    assert r.parsed_notes == n
    for t in r.tickets:
        assert len(t.front) == 5 and len(t.back) == 2


@pytest.mark.parametrize("seed", range(15))
def test_slash_prize_flow_matrix(seed, task_storage):
    import random
    rng = random.Random(seed)
    n = rng.randint(2, 6)
    notes = []
    for _ in range(n):
        f = sorted(rng.sample(range(1, 36), 5))
        b = sorted(rng.sample(range(1, 13), 2))
        notes.append(" ".join(f"{x:02d}" for x in f) + "+ " + " ".join(f"{x:02d}" for x in b))
    s = " / ".join(notes)
    r1 = handle_query(f"7月31日买了{n}组：{s}")
    assert f"{n} 注" in r1 or "是否按" in r1
