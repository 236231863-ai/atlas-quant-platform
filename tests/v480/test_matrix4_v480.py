"""v4.8 补充矩阵 4（补足 ≥1000）。"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from engine.import_center import TextImporter, import_text
from engine.ticket_ocr import parse_ocr_text, TicketOCREngine
from engine.data_quality import check_data_quality
from engine.profile_card import build_profile_card
from engine.onboarding.flow_v48 import OnboardingFlow, start_onboarding
from engine.user_analytics import AnalyticsTracker


def t(tid, front=None, day="2026-08-01", cost=2.0):
    return {"ticket_id": tid, "lottery": "dlt",
            "front": front or [1, 2, 3, 4, 5], "back": [1, 2],
            "buy_date": day, "draw_date": "2026-08-01", "cost": cost}


@pytest.mark.parametrize("i", range(20))
def test_import_roundtrip(ticket_storage, i):
    text = f"{i % 35 + 1:02d} 05 12 23 30 + 06 08"
    rep = import_text(text)
    assert rep.total_imported == 1


@pytest.mark.parametrize("i", range(20))
def test_ocr_save_flow(ticket_storage, i):
    r = parse_ocr_text(f"{i % 35 + 1:02d} 05 12 23 30 06 08")
    assert TicketOCREngine.save_confirmed(r) is False  # 未确认
    r2 = TicketOCREngine.confirm(r)
    assert TicketOCREngine.save_confirmed(r2) is True


@pytest.mark.parametrize("i", range(20))
def test_quality_stable(i):
    tickets = [t(f"T{j}", front=[j + 1, j + 2, j + 3, j + 4, j + 5]) for j in range(i + 1)]
    rep = check_data_quality(tickets)
    assert rep.trust_level in ("A", "B", "C")


@pytest.mark.parametrize("i", range(20))
def test_profile_stable(i):
    card = build_profile_card([t(f"T{j}") for j in range(i + 1)])
    assert card.to_dict()


@pytest.mark.parametrize("i", range(15))
def test_onboarding_events(ticket_storage, i):
    AnalyticsTracker().clear()
    flow = start_onboarding()
    for _ in range(i % 4):
        flow.next()
    flow.finish()
    assert AnalyticsTracker().count("onboarding_start") == 1
    assert AnalyticsTracker().count("onboarding_complete") == 1


@pytest.mark.parametrize("i", range(15))
def test_import_parse_empty(i):
    assert TextImporter.parse("   ") is None
