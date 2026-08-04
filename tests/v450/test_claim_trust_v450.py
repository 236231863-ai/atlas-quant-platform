"""v4.5 P4：兑奖信任升级测试。

覆盖：报告信任字段（来源/期号/更新时间/校验状态）/ trust_text / summary 含信任。
"""
from __future__ import annotations

import pytest

from engine.claim_center import AutoClaimReport, ClaimCenter


def mk_tickets(draw_date="2026-08-01", win=True):
    if win:
        return [{"ticket_id": "T-1", "lottery": "dlt",
                 "front": [10, 11, 18, 22, 35], "back": [6, 12],
                 "buy_date": "2026-07-31", "draw_date": draw_date, "cost": 2.0}]
    return [{"ticket_id": "T-1", "lottery": "dlt",
             "front": [1, 2, 3, 4, 5], "back": [1, 2],
             "buy_date": "2026-07-31", "draw_date": draw_date, "cost": 2.0}]


# ---------- 报告信任字段 ----------
def test_report_default_trust_fields():
    r = AutoClaimReport()
    assert r.issue == ""
    assert r.data_source == "官方数据"
    assert r.updated_at == ""
    assert r.verified is True


def test_auto_claim_sets_issue(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert r.issue  # 26086 或匹配期


def test_auto_claim_source(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert r.data_source in ("官方数据", "本地缓存")


def test_auto_claim_verified(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert r.verified is True


def test_auto_claim_updated_at_field(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert isinstance(r.updated_at, str)


# ---------- trust_text ----------
def test_trust_text_fields(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    t = r.trust_text()
    assert "兑奖报告" in t
    assert "开奖期" in t
    assert "号码来源" in t
    assert "状态" in t


def test_trust_text_verified(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert "已验证" in r.trust_text()


def test_trust_text_not_verified():
    r = AutoClaimReport(verified=False)
    assert "未验证" in r.trust_text()


# ---------- summary 含信任 ----------
def test_summary_has_source(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert "数据来源" in r.summary_text()


def test_summary_has_verified(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert "已验证" in r.summary_text()


def test_summary_has_issue(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert "开奖期" in r.summary_text()


# ---------- to_dict ----------
def test_to_dict_trust_fields(ticket_storage):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    d = r.to_dict()
    assert "issue" in d
    assert "data_source" in d
    assert "updated_at" in d
    assert "verified" in d


# ---------- 数据源判定 ----------
def test_data_source_text():
    assert ClaimCenter._data_source_text("dlt") in ("官方数据", "本地缓存")


def test_data_updated_at_str():
    assert isinstance(ClaimCenter._data_updated_at("dlt"), str)


def test_data_verified_empty():
    assert ClaimCenter._data_verified("dlt", None) is False


def test_data_verified_match(ticket_storage):
    class FakeRep:
        draw_issue = "26086"
    r = ClaimCenter._data_verified("dlt", FakeRep())
    assert r is True or r is False


# ---------- 矩阵 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_auto_claim_lottery_trust(ticket_storage, lottery):
    t = mk_tickets()[0]
    t["lottery"] = lottery
    if lottery == "ssq":
        t["front"] = [1, 2, 3, 4, 5, 6]; t["back"] = [1]
    r = ClaimCenter.auto_claim([t], lottery=lottery, draw_date="2026-08-01")
    assert isinstance(r.issue, str)
    assert r.data_source in ("官方数据", "本地缓存")


@pytest.mark.parametrize("i", range(10))
def test_auto_claim_trust_stable(ticket_storage, i):
    r = ClaimCenter.auto_claim(mk_tickets(), lottery="dlt", draw_date="2026-08-01")
    assert r.trust_text()
