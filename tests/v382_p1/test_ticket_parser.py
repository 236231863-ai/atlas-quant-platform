"""v3.8.2-P1 Phase 2：连续号码解析（含 100 组随机）。"""
from __future__ import annotations

import random

import pytest

from engine.lottery_intent.ticket_parser import TicketParser


def _build_notes(notes):
    """notes: [(front, back), ...] → 连续号码串（空格分隔每注）。"""
    return " ".join("".join(f"{n:02d}" for n in row) for t in notes for row in t)


# ---------- 任务书场景 ----------
@pytest.mark.parametrize("continuous,front,back", [
    ("13212326330112", [13, 21, 23, 26, 33], [1, 12]),
    ("01020304050607", [1, 2, 3, 4, 5], [6, 7]),
    ("10111822350612", [10, 11, 18, 22, 35], [6, 12]),
])
def test_single_continuous_note(continuous, front, back):
    r = TicketParser.parse(continuous)
    assert r.parsed_notes == 1
    assert r.tickets[0].front == front
    assert r.tickets[0].back == back


def test_two_continuous_notes():
    r = TicketParser.parse("13212326330112 01020304050607")
    assert r.parsed_notes == 2
    assert r.tickets[0].front == [13, 21, 23, 26, 33]
    assert r.tickets[1].front == [1, 2, 3, 4, 5]
    assert r.tickets[1].back == [6, 7]


def test_15_notes():
    fronts = [[10, 11, 18, 22, 35], [1, 2, 3, 4, 5], [5, 10, 15, 20, 25],
              [3, 4, 14, 28, 31], [13, 25, 30, 32, 33]]
    notes = [(f, [6, 12]) for f in fronts] + [(f, [2, 7]) for f in fronts] + [(f, [3, 9]) for f in fronts]
    s = _build_notes(notes)
    r = TicketParser.parse(s)
    assert r.parsed_notes == 15
    assert r.tickets[0].front == [10, 11, 18, 22, 35]
    assert r.tickets[-1].back == [3, 9]


def test_30_notes():
    fronts = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
    notes = [(f, [1, 2]) for f in fronts] * 15
    r = TicketParser.parse(_build_notes(notes))
    assert r.parsed_notes == 30


def test_100_notes():
    fronts = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15],
              [16, 17, 18, 19, 20], [21, 22, 23, 24, 25]]
    notes = [(f, [1, 2]) for f in fronts] * 20
    r = TicketParser.parse(_build_notes(notes))
    assert r.parsed_notes == 100


def test_date_not_parsed_as_numbers():
    """日期与量词不得混入号码（7月31日 / 15组）。"""
    fronts = [[10, 11, 18, 22, 35], [1, 2, 3, 4, 5]]
    notes = [(f, [6, 12]) for f in fronts]
    s = _build_notes(notes)
    r = TicketParser.parse(f"7月31日购买了这{len(notes)}组，我能获得多少奖金：{s}")
    assert r.parsed_notes == 2
    assert r.buy_date == "07-31"


# ---------- 传统格式回归 ----------
@pytest.mark.parametrize("text,f,b", [
    ("01 02 03 04 05 + 06 07", [1, 2, 3, 4, 5], [6, 7]),
    ("前区 01 02 03 04 05 后区 06 07", [1, 2, 3, 4, 5], [6, 7]),
    ("05,10,15,20,25|08,09", [5, 10, 15, 20, 25], [8, 9]),
    ("10 11 18 22 35 06 12", [10, 11, 18, 22, 35], [6, 12]),
])
def test_traditional_formats(text, f, b):
    r = TicketParser.parse(text)
    assert r.parsed_notes == 1
    assert r.tickets[0].front == f
    assert r.tickets[0].back == b


# ---------- 100 组随机号码 ----------
@pytest.fixture(scope="module")
def random_groups():
    groups = []
    rng = random.Random(20260802)
    for _ in range(100):
        notes = []
        for __ in range(rng.randint(1, 8)):
            f = sorted(rng.sample(range(1, 36), 5))
            b = sorted(rng.sample(range(1, 13), 2))
            notes.append((f, b))
        groups.append(notes)
    return groups


@pytest.mark.parametrize("i", list(range(100)))
def test_random_100(i, random_groups):
    notes = random_groups[i]
    s = _build_notes(notes)
    r = TicketParser.parse(s)
    assert r.parsed_notes == len(notes)
    for j, t in enumerate(r.tickets):
        assert t.front == notes[j][0], f"组{i} 注{j} 前区不符"
        assert t.back == notes[j][1], f"组{i} 注{j} 后区不符"


# ---------- 结构化输出 ----------
def test_to_ticket_dicts():
    r = TicketParser.parse("13212326330112")
    d = r.to_ticket_dicts()
    assert d == [{"front": [13, 21, 23, 26, 33], "back": [1, 12]}]


def test_parsed_notes_field():
    r = TicketParser.parse("01 02 03 04 05 + 06 07；01 02 03 04 05 + 06 08")
    assert r.parsed_notes == 2


def test_empty_input():
    r = TicketParser.parse("")
    assert r.parsed_notes == 0
    assert not r.is_viable
