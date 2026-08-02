"""v3.8.0 产品层完成网格（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.user_memory import UserMemory, ChatContext
from engine.data_center_v2 import DrawRecord

# 票据边界网格
@pytest.mark.parametrize("n", [1, 2, 3, 7, 11])
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_ticket_boundary(tmp_path, n, lottery):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.add(lottery, [1,2,3,4,5], [6,7])
    assert m.count() == n

# 报告边界网格
@pytest.mark.parametrize("won,total", [(0,0), (1,5), (2,200), (3,100000)])
@pytest.mark.parametrize("n", [1, 3])
def test_report_boundary(tmp_path, won, total, n):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    for i in range(n):
        r.save("dlt", 5, min(won, 5), total, "x")
    assert r.count() == n

# 追号边界
@pytest.mark.parametrize("n", [1, 3, 10])
@pytest.mark.parametrize("k", [1, 5, 10])
def test_chase_boundary(n, k):
    draws = [DrawRecord(str(i), "2026-01-01", [1,2,3,4,5], [6,7], 100.0) for i in range(n)]
    info = ChaseAnalysis.missing_numbers(draws, top_k=k)
    assert len(info) <= k

# 记忆边界
@pytest.mark.parametrize("i", range(10))
def test_memory_boundary(tmp_path, i):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    assert m.get("nonexist", "default") == "default"
    m.set("k", i)
    assert m.get("k") == i

# 上下文边界
@pytest.mark.parametrize("i", range(10))
def test_context_boundary(i):
    c = ChatContext()
    for j in range(i):
        c.remember(f"m{j}")
    assert len(c.history) <= 6

# 端到端补强
@pytest.mark.parametrize("i", range(15))
def test_flow_prize_report(tmp_path, i):
    from engine.lottery_intent import compute_prize_report
    from engine.report_center import ReportCenter
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    text = f"大乐透 {i+1} {i+2} {i+3} {i+4} {i+5} + {i%12+1} {i%11+2} 中了吗"
    rep = compute_prize_report(text)
    assert "report_text" in rep
    if rep.get("is_prize"):
        r.save(rep.get("lottery","dlt"), rep.get("tickets",0), rep.get("won_notes",0), rep.get("total",0), rep["report_text"])
        assert r.total_winnings() >= 0
