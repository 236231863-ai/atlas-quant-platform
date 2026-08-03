"""v4.1.1 补足：用户留存闭环流程测试。"""
from __future__ import annotations

import random

import pytest

from engine.assistant import handle_query
from engine.reminder_center import today_reminders
from engine.budget_manager import BudgetPlanner


@pytest.fixture()
def ticket_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("engine.ticket_system.manager.os.path.expanduser",
                        lambda *a, **k: str(tmp_path))
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    monkeypatch.setenv("ATLAS_TASK_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


def _seed(n=3, win=False):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(n):
        if win and i == 0:
            mgr.add("dlt", [10, 11, 18, 22, 35], [6, 12],
                    buy_date="2026-07-31", draw_date="2026-08-01")
        else:
            mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01")
    return mgr


# ---------- 留存闭环流程 ----------
def test_retention_loop(ticket_storage):
    """留存闭环：保存→提醒→兑奖→预算→成长。"""
    from engine.ticket_system import TicketManager
    _seed(3)
    # 提醒
    tickets = [t.__dict__ for t in TicketManager().list_all()]
    r = today_reminders(tickets)
    assert isinstance(r.notify_text(), str)
    # 预算提醒
    tips = BudgetPlanner.reminders(tickets)
    assert isinstance(tips, list)
    TicketManager().clear()


def test_full_retention_flow(ticket_storage):
    _seed(3, win=True)
    # AI 兑奖
    r1 = handle_query("帮我复盘一下")
    assert "投入" in r1 or "中奖" in r1
    # 提醒
    from engine.ticket_system import TicketManager
    r2 = today_reminders([t.__dict__ for t in TicketManager().list_all()])
    assert r2.prize_due >= 0
    TicketManager().clear()


@pytest.mark.parametrize("seed", range(20))
def test_retention_flow_matrix(seed, ticket_storage):
    rng = random.Random(seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    for i in range(rng.randint(1, 6)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7],
                buy_date=f"2026-08-{i + 1:02d}",
                draw_date="2026-08-05" if rng.random() < 0.5 else "")
    tickets = [t.__dict__ for t in mgr.list_all()]
    r = today_reminders(tickets)
    assert r.notify_text()
    assert sum(r.ticket_status.values()) == len(tickets)
    mgr.clear()


@pytest.mark.parametrize("seed", range(15))
def test_budget_reminder_flow(seed, ticket_storage):
    rng = random.Random(1000 + seed)
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.clear()
    cost = rng.choice([10, 20, 50, 100])
    for i in range(rng.randint(1, 8)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01", cost=cost)
    tips = BudgetPlanner.reminders([t.__dict__ for t in mgr.list_all()])
    assert isinstance(tips, list)
    mgr.clear()
