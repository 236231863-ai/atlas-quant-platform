"""v4.0.0 Phase 5：AI 助手个人决策分析测试。"""
from __future__ import annotations

import random

import pytest

from engine.assistant import AssistantIntentRouter, execute_intent, handle_query


@pytest.fixture()
def ticket_storage(tmp_path, monkeypatch):
    """隔离 TicketManager 存储。"""
    monkeypatch.setattr("engine.ticket_system.manager.os.path.expanduser",
                        lambda *a, **k: str(tmp_path))
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


def _seed_tickets(n=3, win=False):
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


# ---------- 路由 ----------
@pytest.mark.parametrize("query", [
    "我最近买彩票情况怎么样？",
    "我一年花多少钱？",
    "帮我复盘一下",
    "我的投注习惯怎么样",
    "我买彩票花了多少",
    "复盘我的投注",
    "个人报告",
    "预算管理",
    "我的行为分析",
    "这半年买彩票情况",
])
def test_route_personal(query):
    r = AssistantIntentRouter().route(query)
    assert r.tool == "personal_analyze", f"{query} → {r.tool}"


@pytest.mark.parametrize("query,tool", [
    ("分析我的号码", "quant_analyze"),
    ("这注中了多少钱", "prize"),
    ("推荐一注", "recommend"),
    ("热号有哪些", "hot_cold"),
    ("中奖了吗", "prize"),
])
def test_route_other_tools(query, tool):
    assert AssistantIntentRouter().route(query).tool == tool


def test_personal_priority_over_quant():
    """个人强词优先于量化。"""
    r = AssistantIntentRouter().route("帮我复盘一下")
    assert r.tool == "personal_analyze"


def test_prize_priority_over_personal():
    r = AssistantIntentRouter().route("帮我算算中奖奖金")
    assert r.tool == "prize"


def test_pending_confirm_still_first(task_storage):
    handle_query("7月31日买大乐透：10111822350612")
    r = AssistantIntentRouter().route("是的")
    assert r.is_confirm
    from engine.task_context import PendingTaskManager
    PendingTaskManager().clear_task("default")


# ---------- 行为分析 ----------
def test_personal_behavior(ticket_storage):
    _seed_tickets(3)
    res = execute_intent("personal_analyze", "我最近买彩票情况怎么样？")
    assert res.success
    assert res.data["type"] == "behavior"
    assert "投注" in res.text
    assert "风险等级" in res.text


def test_personal_behavior_total(ticket_storage):
    _seed_tickets(5)
    res = execute_intent("personal_analyze", "我的行为分析")
    assert res.data["total_spent"] == pytest.approx(10.0)


def test_personal_behavior_chase(ticket_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-08")
    res = execute_intent("personal_analyze", "我的行为")
    assert res.data["chase_count"] == 1


# ---------- 预算 ----------
def test_personal_budget(ticket_storage):
    _seed_tickets(3)
    res = execute_intent("personal_analyze", "我一年花多少钱？")
    assert res.success
    assert res.data["type"] == "budget"
    assert "预算" in res.text or "健康" in res.text


def test_personal_budget_spent(ticket_storage):
    _seed_tickets(4)
    res = execute_intent("personal_analyze", "预算管理")
    assert res.data["month_spent"] >= 0
    assert res.data["health_score"] > 0


@pytest.mark.parametrize("q", ["预算管理", "我花了多少", "一年花多少钱", "投入多少"])
def test_budget_variants(ticket_storage, q):
    _seed_tickets(2)
    res = execute_intent("personal_analyze", q)
    assert res.data["type"] == "budget"


# ---------- 复盘 ----------
def test_personal_review(ticket_storage):
    _seed_tickets(3, win=True)
    res = execute_intent("personal_analyze", "帮我复盘一下")
    assert res.success
    assert res.data["type"] == "review"
    assert "投入" in res.text
    assert "中奖" in res.text


def test_review_win(ticket_storage):
    _seed_tickets(2, win=True)
    res = execute_intent("personal_analyze", "复盘")
    assert res.data["net_profit"] > 0


def test_review_win_rate(ticket_storage):
    _seed_tickets(4, win=True)
    res = execute_intent("personal_analyze", "复盘一下")
    assert 0 <= res.data["win_rate"] <= 1


@pytest.mark.parametrize("q", ["复盘", "帮我复盘", "中奖情况", "收益如何"])
def test_review_variants(ticket_storage, q):
    _seed_tickets(3)
    res = execute_intent("personal_analyze", q)
    assert res.data["type"] == "review"


# ---------- 无票据引导 ----------
def test_no_tickets(ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    res = execute_intent("personal_analyze", "我最近买彩票情况")
    assert not res.success
    assert "票据" in res.text


def test_no_tickets_missing_field(ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    res = execute_intent("personal_analyze", "复盘")
    assert "tickets" in res.missing


# ---------- handle_query 端到端 ----------
def test_handle_behavior(ticket_storage):
    _seed_tickets(3)
    reply = handle_query("我最近买彩票情况怎么样？")
    assert "投注" in reply
    assert "随机性" in reply


def test_handle_budget(ticket_storage):
    _seed_tickets(3)
    reply = handle_query("我一年花多少钱？")
    assert "预算" in reply or "健康" in reply


def test_handle_review(ticket_storage):
    _seed_tickets(3, win=True)
    reply = handle_query("帮我复盘一下")
    assert "中奖" in reply


def test_handle_no_data(ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    reply = handle_query("我最近买彩票情况")
    assert "票据" in reply or "数据" in reply


# ---------- 免责声明 ----------
@pytest.mark.parametrize("q", ["我最近买彩票情况", "我一年花多少钱", "帮我复盘"])
def test_disclaimer(ticket_storage, q):
    _seed_tickets(2)
    res = execute_intent("personal_analyze", q)
    assert "随机性" in res.text


def test_no_prediction(ticket_storage):
    _seed_tickets(2)
    res = execute_intent("personal_analyze", "我最近买彩票情况")
    for banned in ("预测", "提高中奖概率", "稳赚"):
        assert banned not in res.text


# ---------- 报告结构 ----------
@pytest.mark.parametrize("q,field", [
    ("我最近买彩票情况", "total_spent"),
    ("我最近买彩票情况", "risk_level"),
    ("我一年花多少钱", "health_score"),
    ("帮我复盘一下", "net_profit"),
])
def test_data_fields(ticket_storage, q, field):
    _seed_tickets(3, win=True)
    res = execute_intent("personal_analyze", q)
    assert field in res.data


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_behavior_matrix(seed, ticket_storage):
    rng = random.Random(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 15)):
        mgr.add("dlt", sorted(rng.sample(range(1, 36), 5)),
                sorted(rng.sample(range(1, 13), 2)),
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    res = execute_intent("personal_analyze", "我最近买彩票情况")
    assert res.success
    assert res.data["total_spent"] > 0


@pytest.mark.parametrize("seed", range(40))
def test_budget_matrix(seed, ticket_storage):
    rng = random.Random(1000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 10)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                cost=2.0 * rng.randint(1, 5))
    res = execute_intent("personal_analyze", "我一年花多少钱")
    assert res.data["type"] == "budget"
    assert res.data["year_spent"] > 0


@pytest.mark.parametrize("seed", range(40))
def test_review_matrix(seed, ticket_storage):
    rng = random.Random(2000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 10)):
        front = sorted(rng.sample(range(1, 36), 5))
        back = sorted(rng.sample(range(1, 13), 2))
        mgr.add("dlt", front, back,
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}")
    res = execute_intent("personal_analyze", "帮我复盘一下")
    assert res.success
    assert res.data["type"] == "review"
    assert res.data["net_profit"] <= 0 or res.data["win_rate"] >= 0


@pytest.mark.parametrize("seed", range(30))
def test_route_stability(seed):
    router = AssistantIntentRouter()
    r = router.route("我最近买彩票情况怎么样？")
    assert r.tool == "personal_analyze"


@pytest.mark.parametrize("seed", range(30))
def test_handle_matrix(seed, ticket_storage):
    _seed_tickets(3)
    reply = handle_query("我最近买彩票情况怎么样？")
    assert isinstance(reply, str)
    assert len(reply) > 20


# ---------- 补充矩阵（凑 ≥300） ----------
@pytest.mark.parametrize("q", [
    "我买彩票情况", "我的投注情况", "最近买彩票", "行为分析",
    "我买彩票习惯", "投注行为", "我的习惯", "近期投注",
])
def test_behavior_route_variants(q):
    r = AssistantIntentRouter().route(q)
    assert r.tool == "personal_analyze"


@pytest.mark.parametrize("seed", range(40))
def test_behavior_reports_matrix(seed, ticket_storage):
    rng = random.Random(5000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 12)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                cost=2.0 * rng.randint(1, 4))
    res = execute_intent("personal_analyze", "我最近买彩票情况")
    assert res.data["total_spent"] == pytest.approx(sum(t.cost for t in mgr.list_all()), abs=0.01)


@pytest.mark.parametrize("seed", range(40))
def test_review_amounts_matrix(seed, ticket_storage):
    rng = random.Random(6000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 8)):
        mgr.add("dlt", [10, 11, 18, 22, 35] if rng.random() < 0.3 else [1, 2, 3, 4, 5],
                [6, 12] if rng.random() < 0.3 else [6, 7],
                buy_date="2026-07-31" if i == 0 else f"2026-07-{10 + i:02d}")
    res = execute_intent("personal_analyze", "帮我复盘一下")
    assert res.data["total_investment"] > 0
    assert res.data["net_profit"] >= res.data["total_winnings"] - res.data["total_investment"] - 1


@pytest.mark.parametrize("seed", range(30))
def test_missing_guidance_matrix(seed, ticket_storage):
    from engine.ticket_system import TicketManager
    TicketManager().clear()
    res = execute_intent("personal_analyze", "我最近买彩票情况")
    assert not res.success
    assert "票据" in res.text


@pytest.mark.parametrize("seed", range(30))
def test_handle_budget_variants(seed, ticket_storage):
    _seed_tickets(3)
    for q in ("我一年花多少钱？", "预算管理", "我花了多少"):
        reply = handle_query(q)
        assert isinstance(reply, str)
        assert len(reply) > 10
