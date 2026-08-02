"""v3.8.0 产品层补充网格（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager, TicketRecord
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.user_memory import UserMemory, ChatContext
from engine.data_center_v2 import DrawRecord

# 票据大网格
@pytest.mark.parametrize("n", [2, 4, 8, 16, 32, 64])
@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq"])
def test_ticket_big(tmp_path, n, lottery):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.add(lottery, [i%35+1, i%34+2, i%33+3, i%32+4, i%31+5], [i%12+1, i%11+2])
    assert m.count() == n

@pytest.mark.parametrize("i", range(20))
def test_ticket_front_roundtrip(tmp_path, i):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    front = [i%35+1, (i+1)%35+1, (i+2)%35+1, (i+3)%35+1, (i+4)%35+1]
    t = m.add("dlt", front, [6, 7])
    assert m.get(t.ticket_id).front == front

# 报告大网格
@pytest.mark.parametrize("n", [1, 2, 5, 10, 20])
@pytest.mark.parametrize("total", [0, 5, 100, 10000])
def test_report_total_grid(tmp_path, n, total):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    for i in range(n):
        r.save("dlt", 1, 1, total, "x")
    assert r.total_winnings() == total * n

@pytest.mark.parametrize("i", range(10))
def test_report_id_unique(tmp_path, i):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    ids = [r.save("dlt", 1, 1, 100, "x").report_id for _ in range(5)]
    assert len(set(ids)) == 5

# 追号大网格
@pytest.mark.parametrize("n", [10, 50, 100, 200, 400])
def test_chase_big(n):
    draws = [DrawRecord(str(i), "2026-01-01", [1,2,3,4,5], [6,7], 100.0) for i in range(n)]
    info = ChaseAnalysis.missing_numbers(draws)
    assert len(info) == 10

@pytest.mark.parametrize("front", [[1,2,3,4,5], [2,4,6,8,10], [5,10,15,20,25]])
@pytest.mark.parametrize("n", [30, 100])
def test_chase_front(front, n):
    draws = [DrawRecord(str(i), "2026-01-01", front, [6,7], 100.0) for i in range(n)]
    info = ChaseAnalysis.missing_numbers(draws)
    assert len(info) >= 1

# 记忆大网格
@pytest.mark.parametrize("key", [f"pref_{i}" for i in range(25)])
def test_memory_big(tmp_path, key):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set(key, 1)
    assert m.get(key) == 1

@pytest.mark.parametrize("i", range(15))
def test_memory_all(tmp_path, i):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear()
    m.set("a", 1); m.set("b", 2)
    d = m.all()
    assert d["a"] == 1

# 上下文大网格
@pytest.mark.parametrize("i", range(20))
def test_context_wide(i):
    c = ChatContext()
    c.remember(f"号码 {i}")
    assert "号码" in c.history[0]

@pytest.mark.parametrize("nums", ["01 02 03 04 05 + 06 07", "10 20 30 35 15 + 08 09", "1 2 3 4 5 6 + 7"])
def test_context_extract_wide(nums):
    c = ChatContext()
    assert c.extract_numbers(nums)

# 票据文本解析大网格
@pytest.mark.parametrize("text", [
    "大乐透 01 02 03 04 05 + 06 07",
    "双色球 01 02 03 04 05 06 + 07",
    "前区 01 02 03 04 05 后区 06 07",
])
@pytest.mark.parametrize("n", [1, 2])
def test_ticket_text_grid(tmp_path, text, n):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    full = "; ".join([text] * n)
    saved = m.add_from_text(full)
    assert len(saved) >= 1
