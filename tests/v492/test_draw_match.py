"""奖级匹配测试：覆盖大乐透全部 13 个中奖组合。"""
from __future__ import annotations

import pytest

from backend.mobile.service import DrawMatcher

DRAW_FRONT = [10, 11, 18, 22, 35]
DRAW_BACK = [6, 12]


def _m(front, back):
    return DrawMatcher.match(front, back, DRAW_FRONT, DRAW_BACK)


class TestPrizeMatch:
    def test_first_prize_5_2(self):
        r = _m([10, 11, 18, 22, 35], [6, 12])
        assert r["won"] and r["level"] == "一等奖" and r["amount"] == 10000000

    def test_second_prize_5_1(self):
        r = _m([10, 11, 18, 22, 35], [6, 5])
        assert r["level"] == "二等奖" and r["amount"] == 500000

    def test_third_prize_5_0(self):
        r = _m([10, 11, 18, 22, 35], [1, 3])
        assert r["level"] == "三等奖" and r["amount"] == 10000

    def test_fourth_prize_4_2(self):
        r = _m([10, 11, 18, 22, 1], [6, 12])
        assert r["level"] == "四等奖" and r["amount"] == 3000

    def test_fifth_prize_4_1(self):
        r = _m([10, 11, 18, 22, 1], [6, 5])
        assert r["level"] == "五等奖" and r["amount"] == 300

    def test_sixth_prize_3_2(self):
        r = _m([10, 11, 18, 1, 2], [6, 12])
        assert r["level"] == "六等奖" and r["amount"] == 200

    def test_seventh_prize_4_0(self):
        r = _m([10, 11, 18, 22, 1], [1, 3])
        assert r["level"] == "七等奖" and r["amount"] == 100

    def test_eighth_prize_3_1(self):
        r = _m([10, 11, 18, 1, 2], [6, 5])
        assert r["level"] == "八等奖" and r["amount"] == 15

    def test_eighth_prize_2_2(self):
        r = _m([10, 11, 1, 2, 3], [6, 12])
        assert r["level"] == "八等奖" and r["amount"] == 15

    def test_ninth_prize_3_0(self):
        r = _m([10, 11, 18, 1, 2], [1, 3])
        assert r["level"] == "九等奖" and r["amount"] == 5

    def test_ninth_prize_1_2(self):
        r = _m([10, 1, 2, 3, 4], [6, 12])
        assert r["level"] == "九等奖" and r["amount"] == 5

    def test_ninth_prize_2_1(self):
        r = _m([10, 11, 1, 2, 3], [6, 5])
        assert r["level"] == "九等奖" and r["amount"] == 5

    def test_ninth_prize_0_2(self):
        # 用户真实案例：后区全中 0+2 → 九等奖
        r = _m([6, 16, 21, 30, 34], [6, 12])
        assert r["won"] and r["level"] == "九等奖" and r["amount"] == 5


class TestNoWin:
    def test_no_hit(self):
        r = _m([1, 2, 3, 4, 5], [1, 3])
        assert not r["won"] and r["level"] is None and r["amount"] == 0

    def test_1_0_no_win(self):
        r = _m([10, 1, 2, 3, 4], [1, 3])
        assert not r["won"]

    def test_0_1_no_win(self):
        r = _m([1, 2, 3, 4, 5], [6, 1])
        assert not r["won"]

    def test_2_0_no_win(self):
        r = _m([10, 11, 1, 2, 3], [1, 3])
        assert not r["won"]

    def test_hit_counts_reported(self):
        r = _m([10, 11, 1, 2, 3], [6, 5])
        assert r["front_hit"] == 2 and r["back_hit"] == 1
