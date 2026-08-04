"""v4.8 大规模矩阵 2：quality/profile/onboarding 参数化。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.data_quality import check_data_quality
from engine.profile_card import build_profile_card


def t(tid, front=None, day="2026-08-01", cost=2.0, win=False):
    if win:
        return {"ticket_id": tid, "lottery": "dlt",
                "front": [10, 11, 18, 22, 35], "back": [6, 12],
                "buy_date": day, "draw_date": "2026-08-01", "cost": cost}
    return {"ticket_id": tid, "lottery": "dlt",
            "front": front or [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


# ---------- quality 矩阵 ----------
@pytest.mark.parametrize("i", range(30))
def test_quality_clean_unique(i):
    tickets = [t(f"T{j}", front=[j + 1, j + 2, j + 3, j + 4, j + 5]) for j in range(i + 1)]
    rep = check_data_quality(tickets)
    assert rep.duplicates == 0
    assert rep.trust_level == "A"


@pytest.mark.parametrize("i", range(30))
def test_quality_dup_scale(i):
    tickets = [t(f"T{j}") for j in range(i + 1)]
    rep = check_data_quality(tickets)
    assert rep.duplicates == i


@pytest.mark.parametrize("i", range(20))
def test_quality_invalid(i):
    rep = check_data_quality([t("T1", front=[1, 2, 3, 4])])
    assert rep.invalid_numbers == 1


@pytest.mark.parametrize("i", range(20))
def test_quality_future(i):
    future = (date.today() + timedelta(days=i + 1)).isoformat()
    rep = check_data_quality([t("T1", day=future)])
    assert rep.date_anomalies == 1


# ---------- profile 矩阵 ----------
@pytest.mark.parametrize("i", range(30))
def test_profile_age(i):
    day = (date.today() - timedelta(days=i * 10)).isoformat()
    card = build_profile_card([t("T1", day=day)])
    assert card.lottery_age_days >= i * 10 - 1


@pytest.mark.parametrize("i", range(1, 31))
def test_profile_tickets(i):
    tickets = [t(f"T{j}", day=f"2026-08-{j % 28 + 1:02d}") for j in range(i)]
    card = build_profile_card(tickets)
    assert card.total_tickets == i
    assert card.total_investment == i * 2.0


@pytest.mark.parametrize("i", range(20))
def test_profile_win(i):
    card = build_profile_card([t("T1", win=True)])
    assert card.best_win >= 5_000_000


@pytest.mark.parametrize("i", range(30))
def test_profile_risk_valid(i):
    tickets = [t(f"T{j}") for j in range(i + 1)]
    card = build_profile_card(tickets)
    assert card.risk_level in ("A", "B", "C")
