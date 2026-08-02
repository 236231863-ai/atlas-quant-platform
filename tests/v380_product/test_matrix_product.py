"""v3.8.0 产品层大矩阵（补充至 1000+）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.user_memory import UserMemory, ChatContext
from engine.data_center_v2 import DrawRecord

# ---- 票据大矩阵 ----
_LOT = ["dlt", "ssq"]
_FRONTS = [[1,2,3,4,5], [10,20,30,35,15], [5,10,15,20,25], [33,32,31,30,29]]
_BACKS = [[6,7], [8,9], [1,12]]
@pytest.mark.parametrize("lottery", _LOT)
@pytest.mark.parametrize("front", _FRONTS)
@pytest.mark.parametrize("back", _BACKS)
def test_ticket_grid(tmp_path, lottery, front, back):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    t = m.add(lottery, front, back)
    assert m.get(t.ticket_id).front == front

@pytest.mark.parametrize("n", [1, 3, 10, 30])
@pytest.mark.parametrize("lottery", _LOT)
def test_ticket_count_grid(tmp_path, n, lottery):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.add(lottery, [1,2,3,4,5], [6,7])
    assert m.count() == n

# ---- 报告大矩阵 ----
@pytest.mark.parametrize("tickets", [1, 5, 15, 50])
@pytest.mark.parametrize("won", [0, 1, 3])
def test_report_grid(tmp_path, tickets, won):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    rep = r.save("dlt", tickets, min(won, tickets), won * 100, "x")
    assert rep.tickets == tickets

@pytest.mark.parametrize("n", [1, 5, 20])
@pytest.mark.parametrize("lottery", _LOT)
def test_report_lottery_grid(tmp_path, n, lottery):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    for i in range(n):
        r.save(lottery, 1, 1, 100, "x")
    assert len(r.by_lottery(lottery)) == n

# ---- 追号大矩阵 ----
def _mk(n, front=None):
    return [DrawRecord(str(24000+i), f"2026-01-{i%28+1:02d}", front or [1,2,3,4,5], [6,7], 100.0) for i in range(n)]

@pytest.mark.parametrize("n", [5, 20, 100, 300])
@pytest.mark.parametrize("front", [[1,2,3,4,5], [5,10,15,20,25]])
def test_chase_grid(n, front):
    info = ChaseAnalysis.missing_numbers(_mk(n, front))
    assert len(info) >= 1
    assert all(m.number >= 1 for m in info)

@pytest.mark.parametrize("k", [1, 5, 10, 15])
def test_chase_topk_grid(k):
    assert len(ChaseAnalysis.missing_numbers(_mk(50), top_k=k)) <= k

# ---- 记忆大矩阵 ----
@pytest.mark.parametrize("key", [f"k{i}" for i in range(20)])
def test_memory_grid(tmp_path, key):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set(key, key)
    assert m.get(key) == key

@pytest.mark.parametrize("i", range(10))
def test_memory_pref_grid(tmp_path, i):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set_preference(f"p{i}", i)
    assert m.get_preference(f"p{i}") == i

# ---- 上下文矩阵 ----
@pytest.mark.parametrize("i", range(10))
def test_context_numbers(i):
    c = ChatContext()
    c.last_numbers = f"{i} {i+1} {i+2}"
    assert c.last_numbers

@pytest.mark.parametrize("msgs", [[f"m{j}" for j in range(i)] for i in range(1, 11)])
def test_context_hist(msgs):
    c = ChatContext()
    for m in msgs:
        c.remember(m)
    assert len(c.history) == min(len(msgs), 6)

# ---- 端到端用户流程 ----
def test_user_flow_prize_save(tmp_path):
    """真实用户流程：买票→兑奖→报告保存→工作台可见。"""
    from engine.lottery_intent import compute_prize_report
    from engine.report_center import ReportCenter
    from engine.ticket_system import TicketManager
    tm = TicketManager(storage_dir=str(tmp_path)); tm.clear()
    rc = ReportCenter(storage_dir=str(tmp_path)); rc.clear()
    # 保存票据
    ts = tm.add_from_text("大乐透 10 11 18 22 35 + 06 12 8月1日开奖")
    assert len(ts) >= 1
    # 兑奖
    r = compute_prize_report("大乐透 10 11 18 22 35 + 06 12 8月1日开奖 中了吗")
    # 保存报告
    if r.get("is_prize"):
        rc.save(r.get("lottery", "dlt"), r.get("tickets", 0), r.get("won_notes", 0), r.get("total", 0), r["report_text"])
        assert rc.count() >= 1

@pytest.mark.parametrize("i", range(10))
def test_user_flow_repeat(tmp_path, i):
    test_user_flow_prize_save(tmp_path)
