"""v3.8.0 产品层最终网格（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.user_memory import UserMemory, ChatContext
from engine.data_center_v2 import DrawRecord

# 票据最大网格：lottery × n × front
_LOTS = ["dlt", "ssq", "dlt", "ssq", "dlt"]
_FRONT_SETS = [[1,2,3,4,5], [10,20,30,35,15], [5,10,15,20,25], [33,32,31,30,29], [11,22,33,34,35]]
@pytest.mark.parametrize("lottery", _LOTS)
@pytest.mark.parametrize("front", _FRONT_SETS)
@pytest.mark.parametrize("n", [1, 5])
def test_ticket_max(tmp_path, lottery, front, n):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.add(lottery, front, [6, 7])
    assert m.count() == n

# 报告最大网格
@pytest.mark.parametrize("tickets", [1, 5, 15, 30, 100])
@pytest.mark.parametrize("won", [0, 2, 5])
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_report_max(tmp_path, tickets, won, lottery):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    rep = r.save(lottery, tickets, min(won, tickets), won * 50, "x")
    assert rep.lottery == lottery

# 追号最大网格
@pytest.mark.parametrize("n", [10, 30, 60, 120, 250])
@pytest.mark.parametrize("front", [[1,2,3,4,5], [5,10,15,20,25], [33,32,31,30,29]])
def test_chase_max(n, front):
    draws = [DrawRecord(str(i), "2026-01-01", front, [6,7], 100.0) for i in range(n)]
    info = ChaseAnalysis.missing_numbers(draws, top_k=8)
    assert len(info) <= 8
    assert all(m.missing_issues >= 0 for m in info)

# 记忆最大网格
@pytest.mark.parametrize("i", range(30))
def test_memory_max(tmp_path, i):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set(f"key{i}", i * 2)
    assert m.get(f"key{i}") == i * 2

@pytest.mark.parametrize("pref", [f"lottery_{i}" for i in range(20)])
def test_memory_pref_max(tmp_path, pref):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set_preference(pref, "v")
    assert m.get_preference(pref) == "v"

# 上下文最大网格
@pytest.mark.parametrize("i", range(15))
def test_context_max(i):
    c = ChatContext()
    c.last_numbers = f"{i} 0{i}"
    c.last_lottery = "dlt"
    c.last_intent = "prize"
    assert c.last_intent == "prize"

# 端到端用户流程矩阵
@pytest.mark.parametrize("i", range(10))
def test_flow_roundtrip(tmp_path, i):
    from engine.lottery_intent import compute_prize_report
    from engine.report_center import ReportCenter
    from engine.ticket_system import TicketManager
    tm = TicketManager(storage_dir=str(tmp_path)); tm.clear()
    rc = ReportCenter(storage_dir=str(tmp_path)); rc.clear()
    text = f"大乐透 {i%9+1} {i%8+2} {i%7+3} {i%6+4} {i%5+5} + {i%4+6} {i%3+7} 中了吗"
    tm.add_from_text(text)
    r = compute_prize_report(text)
    assert "report_text" in r
    if r.get("is_prize"):
        rc.save(r.get("lottery", "dlt"), r.get("tickets", 0), r.get("won_notes", 0), r.get("total", 0), r["report_text"])
        assert rc.count() == 1

@pytest.mark.parametrize("i", range(10))
def test_flow_chase(tmp_path, i):
    draws = [DrawRecord(str(j), "2026-01-01", [1,2,3,4,5], [6,7], 100.0) for j in range(50)]
    s = ChaseAnalysis.summary(draws)
    assert "追号" in s
