"""v4.8 P4：个人彩票档案卡测试。

覆盖：彩票年龄/购买次数/投入/中奖/最佳中奖/连续周期/风险等级。
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.profile_card import ProfileCard, build_profile_card


def t(tid, day, cost=2.0, win=False, lottery="dlt"):
    if win:
        return {"ticket_id": tid, "lottery": lottery,
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": day, "draw_date": "2026-08-01", "cost": cost}
    return {"ticket_id": tid, "lottery": lottery,
            "front": [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- 空 ----------
def test_empty():
    card = build_profile_card([])
    assert card.total_tickets == 0
    assert card.risk_level == "A"


# ---------- 基本指标 ----------
def test_tickets_and_investment():
    card = build_profile_card([t("T1", "2026-08-01"), t("T2", "2026-08-02")])
    assert card.total_tickets == 2
    assert card.total_investment == 4.0


def test_best_win():
    card = build_profile_card([t("T1", "2026-08-01", win=True)])
    assert card.best_win >= 5_000_000
    assert card.total_winnings >= 5_000_000


def test_net():
    card = build_profile_card([t("T1", "2026-08-01"), t("T2", "2026-08-02")])
    assert card.net == -4.0


# ---------- 彩票年龄 ----------
def test_lottery_age():
    day = (date.today() - timedelta(days=30)).isoformat()
    card = build_profile_card([t("T1", day)])
    assert card.lottery_age_days >= 29


def test_first_last_date():
    card = build_profile_card([t("T1", "2026-08-01"), t("T2", "2026-08-05")])
    assert card.first_bet_date == "2026-08-01"
    assert card.last_bet_date == "2026-08-05"


# ---------- 连续周期 ----------
def test_consecutive_months():
    card = build_profile_card([t("T1", "2026-01-05"), t("T2", "2026-02-05"),
                               t("T3", "2026-03-05")])
    assert card.consecutive_periods == 3


# ---------- 风险等级 ----------
def test_risk_negative():
    card = build_profile_card([t("T1", "2026-08-01")] * 5)
    assert card.risk_level in ("A", "B", "C")


def test_risk_all_lose():
    card = build_profile_card([t("T1", "2026-08-01", win=False)] * 10)
    assert card.risk_level in ("B", "C")


# ---------- 常购彩种 ----------
def test_favorite_lottery():
    card = build_profile_card([t("T1", "2026-08-01", lottery="dlt"),
                               t("T2", "2026-08-02", lottery="dlt")])
    assert card.favorite_lottery == "大乐透"


# ---------- 结构 ----------
def test_to_dict():
    card = build_profile_card([t("T1", "2026-08-01")])
    d = card.to_dict()
    assert "lottery_age_days" in d
    assert "risk_level" in d
    assert "net" in d


def test_summary_text():
    card = build_profile_card([t("T1", "2026-08-01")])
    assert "彩票档案卡" in card.summary_text()
    assert "随机性" in card.summary_text()


def test_disclaimer():
    assert "随机性" in ProfileCard().disclaimer


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [0, 1, 5, 10])
def test_scale(n):
    card = build_profile_card([t(f"T{i}", f"2026-08-{i + 1:02d}") for i in range(n)])
    assert card.total_tickets == n
    assert card.total_investment == n * 2.0


@pytest.mark.parametrize("i", range(10))
def test_random(i):
    import random
    random.seed(i)
    tickets = [t(f"T{j}", f"2026-{random.randint(1, 8):02d}-{random.randint(1, 28):02d}",
                 win=random.random() < 0.2) for j in range(random.randint(1, 10))]
    card = build_profile_card(tickets)
    assert card.total_tickets == len(tickets)
    assert card.summary_text()
