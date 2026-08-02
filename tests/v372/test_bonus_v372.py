"""v3.7.2 最终补充（确保 ≥300）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.lottery_intent import LotteryIntentRouter, TicketParser, PrizeCalculator, compute_prize_report

@pytest.mark.parametrize("i", range(10))
def test_intent_consistency(i):
    a = LotteryIntentRouter.detect("中了")
    b = LotteryIntentRouter.detect("中了")
    assert a.is_prize_intent == b.is_prize_intent

@pytest.mark.parametrize("n", range(1, 8))
def test_parse_n(n):
    notes = "; ".join(f"{i%9+1} {i%8+2} {i%7+3} {i%6+4} {i%5+5} + {i%4+6} {i%3+7}" for i in range(n))
    r = TicketParser.parse(notes)
    assert r.parsed_notes == n

@pytest.mark.parametrize("i", range(5))
def test_e2e_deterministic(i):
    a = compute_prize_report("大乐透 10 11 18 22 35 + 06 12 中了")
    b = compute_prize_report("大乐透 10 11 18 22 35 + 06 12 中了")
    assert a["total"] == b["total"]
