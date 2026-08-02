"""v4.0.0 Phase 7：真实用户流程验证（30 秒闭环）。"""
from __future__ import annotations

import random
import time

import pytest

from engine.assistant import handle_query
from engine.lottery_intent.ticket_parser import TicketParser
from engine.lottery_quant.structure import StructureAnalyzer
from engine.lottery_quant.risk import RiskEngine
from engine.personal_review import PersonalReviewEngine
from engine.user_behavior import analyze_behavior
from engine.budget_manager import BudgetPlanner


@pytest.fixture()
def ticket_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("engine.ticket_system.manager.os.path.expanduser",
                        lambda *a, **k: str(tmp_path))
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("ATLAS_TASK_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


NOTES = "10111822350612 01020304050607 05101520250612"


def _save_tickets(n, win=False):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(n):
        if win and i == 0:
            mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12],
                    buy_date="2026-07-31", draw_date="2026-08-01")
        else:
            mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                    buy_date=f"2026-07-{10 + i:02d}")
    return mgr


# ---------- 核心流程（30 秒闭环）----------
def test_full_user_flow(ticket_storage):
    """输入号码→保存票据→分析组合→查看风险→个人报告→设置预算。"""
    t0 = time.time()

    # 1. 输入号码
    parse = TicketParser.parse(NOTES)
    assert parse.parsed_notes == 3

    # 2. 保存票据
    mgr = _save_tickets(3)
    assert mgr.count() == 3

    # 3. 分析组合
    tickets = [t.__dict__ for t in mgr.list_all()]
    s = StructureAnalyzer.analyze([{"front": t["front"], "back": t["back"]} for t in tickets])
    assert 0 <= s.total_score <= 100

    # 4. 查看风险
    risk = RiskEngine.analyze(cost_per_note=2.0, notes_per_draw=3,
                              draws_per_week=3, weeks=52, tickets=tickets, n_years=30)
    assert risk.risk_level in ("A", "B", "C", "D")

    # 5. 个人报告
    rv = PersonalReviewEngine.review(tickets)
    assert rv.total_tickets == 3

    # 6. 设置预算
    bp = BudgetPlanner()
    bp.set_budget(month_budget=300, year_budget=3600)
    assert bp.month_budget == 300

    elapsed = time.time() - t0
    assert elapsed < 30, f"流程超时 {elapsed:.1f}s"
    mgr.clear()


def test_ai_flow(ticket_storage):
    """AI 助手完整流程。"""
    _save_tickets(3)
    reply = handle_query("我最近买彩票情况怎么样？")
    assert "投注" in reply
    reply2 = handle_query("帮我复盘一下")
    assert "中奖" in reply2 or "投入" in reply2
    reply3 = handle_query("我一年花多少钱？")
    assert "预算" in reply3 or "健康" in reply3


# ---------- 各环节独立 ----------
def test_step_parse():
    r = TicketParser.parse(NOTES)
    assert r.parsed_notes == 3
    assert r.lottery == "dlt"


@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_step_save(n, ticket_storage):
    mgr = _save_tickets(n)
    assert mgr.count() == n
    mgr.clear()


@pytest.mark.parametrize("seed", range(20))
def test_step_analyze(seed, ticket_storage):
    rng = random.Random(seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    s = StructureAnalyzer.analyze(tickets)
    assert 0 <= s.total_score <= 100
    assert "随机性" in s.disclaimer


@pytest.mark.parametrize("seed", range(20))
def test_step_risk(seed, ticket_storage):
    rng = random.Random(1000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    risk = RiskEngine.analyze(tickets=tickets, n_years=20, seed=seed)
    assert risk.risk_level in ("A", "B", "C", "D")
    assert risk.lose_probability >= 0


@pytest.mark.parametrize("seed", range(20))
def test_step_review(seed, ticket_storage):
    _save_tickets(5)
    from engine.ticket_system import TicketManager
    rv = PersonalReviewEngine.review_from_manager(TicketManager())
    assert rv.total_tickets == 5
    TicketManager().clear()


@pytest.mark.parametrize("mb", [100, 200, 300, 500])
def test_step_budget(ticket_storage, mb):
    bp = BudgetPlanner()
    bp.set_budget(month_budget=mb)
    assert BudgetPlanner().month_budget == mb


# ---------- 30 秒约束 ----------
def test_flow_within_30s(ticket_storage):
    t0 = time.time()
    for _ in range(5):
        mgr = _save_tickets(5)
        from engine.ticket_system import TicketManager
        tickets = [t.__dict__ for t in TicketManager().list_all()]
        analyze_behavior(tickets)
        PersonalReviewEngine.review(tickets)
        BudgetPlanner().evaluate_tickets(tickets)
        TicketManager().clear()
    assert time.time() - t0 < 30


# ---------- 无预测红线 ----------
@pytest.mark.parametrize("banned", ["预测中奖", "提高中奖概率", "稳赚", "人工智能预测彩票"])
def test_no_prediction_flow(ticket_storage, banned):
    _save_tickets(3)
    for q in ("我最近买彩票情况", "帮我复盘一下", "我一年花多少钱"):
        reply = handle_query(q)
        assert banned not in reply


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_full_flow_matrix(seed, ticket_storage):
    rng = random.Random(seed)
    n = rng.randint(1, 8)
    mgr = _save_tickets(n)
    tickets = [t.__dict__ for t in mgr.list_all()]
    bh = analyze_behavior(tickets)
    assert bh.risk_level in ("A", "B", "C", "D")
    rv = PersonalReviewEngine.review(tickets)
    assert rv.total_tickets == n
    b = BudgetPlanner().evaluate_tickets(tickets)
    assert 0 <= b.health_score <= 100
    mgr.clear()


@pytest.mark.parametrize("seed", range(40))
def test_ai_flow_matrix(seed, ticket_storage):
    rng = random.Random(2000 + seed)
    _save_tickets(rng.randint(1, 6))
    reply = handle_query("我最近买彩票情况怎么样？")
    assert len(reply) > 20
    from engine.ticket_system import TicketManager
    TicketManager().clear()


@pytest.mark.parametrize("seed", range(30))
def test_flow_consistency(seed, ticket_storage):
    rng = random.Random(3000 + seed)
    n = rng.randint(2, 10)
    mgr = _save_tickets(n, win=rng.random() < 0.5)
    tickets = [t.__dict__ for t in mgr.list_all()]
    rv = PersonalReviewEngine.review(tickets)
    assert rv.total_investment == pytest.approx(sum(t["cost"] for t in tickets), abs=0.01)
    assert rv.net_profit == pytest.approx(rv.total_winnings - rv.total_investment, abs=0.01)
    mgr.clear()


@pytest.mark.parametrize("seed", range(30))
def test_step_analyze_no_crash(seed, ticket_storage):
    rng = random.Random(4000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(rng.randint(1, 10))]
    s = StructureAnalyzer.analyze(tickets)
    assert isinstance(s.total_score, int)
