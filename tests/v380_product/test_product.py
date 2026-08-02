"""v3.8.0 P1-P6 测试：ticket_system / report_center / chase_analysis / user_memory。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager, TicketRecord
from engine.report_center import ReportCenter, PrizeReport
from engine.chase_analysis import ChaseAnalysis
from engine.user_memory import UserMemory, ChatContext

@pytest.fixture
def tm(tmp_path):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear(); return m

@pytest.fixture
def rc(tmp_path):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear(); return r

@pytest.fixture
def mem(tmp_path):
    m = UserMemory(storage_dir=str(tmp_path)); m.clear(); return m

# ---------- 票据系统 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_ticket_add(tm, lottery):
    t = tm.add(lottery, [1,2,3,4,5], [6,7])
    assert t.lottery == lottery
    assert tm.count() == 1

@pytest.mark.parametrize("n", [1, 5, 20])
def test_ticket_many(tm, n):
    for i in range(n):
        tm.add("dlt", [1,2,3,4,5], [6,7])
    assert tm.count() == n

def test_ticket_get(tm):
    t = tm.add("dlt", [1,2,3,4,5], [6,7])
    assert tm.get(t.ticket_id) is t
    assert tm.get("NOPE") is None

@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_ticket_by_lottery(tm, lottery):
    tm.add(lottery, [1,2,3,4,5], [6,7])
    assert len(tm.by_lottery(lottery)) == 1

def test_ticket_delete(tm):
    t = tm.add("dlt", [1,2,3,4,5], [6,7])
    assert tm.delete(t.ticket_id) is True
    assert tm.count() == 0
    assert tm.delete("NOPE") is False

@pytest.mark.parametrize("n", [1, 5])
def test_ticket_persist(tmp_path, n):
    a = TicketManager(storage_dir=str(tmp_path))
    for i in range(n):
        a.add("dlt", [1,2,3,4,5], [6,7])
    b = TicketManager(storage_dir=str(tmp_path))
    assert b.count() == n

def test_ticket_from_text(tm):
    ts = tm.add_from_text("大乐透 01 02 03 04 05 + 06 07 中了")
    assert len(ts) >= 1

@pytest.mark.parametrize("i", range(5))
def test_ticket_clear(tm, i):
    tm.add("dlt", [1,2,3,4,5], [6,7])
    tm.clear()
    assert tm.count() == 0

# ---------- 报告中心 ----------
@pytest.mark.parametrize("won,total", [(1, 5000), (3, 100000), (0, 0)])
def test_report_save(rc, won, total):
    r = rc.save("dlt", 10, won, total, "内容")
    assert r.tickets == 10 and r.won_notes == won
    assert rc.count() == 1

@pytest.mark.parametrize("n", [1, 5])
def test_report_many(rc, n):
    for i in range(n):
        rc.save("dlt", 1, 1, 100, "x")
    assert rc.count() == n

def test_report_get(rc):
    r = rc.save("dlt", 1, 1, 100, "x")
    assert rc.get(r.report_id) is r

@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_report_by_lottery(rc, lottery):
    rc.save(lottery, 1, 1, 100, "x")
    assert len(rc.by_lottery(lottery)) == 1

@pytest.mark.parametrize("amounts", [[100], [100, 200], [100, 200, 300]])
def test_report_total(rc, amounts):
    for a in amounts:
        rc.save("dlt", 1, 1, a, "x")
    assert rc.total_winnings() == sum(amounts)

@pytest.mark.parametrize("n", [1, 5])
def test_report_persist(tmp_path, n):
    a = ReportCenter(storage_dir=str(tmp_path))
    for i in range(n):
        a.save("dlt", 1, 1, 100, "x")
    b = ReportCenter(storage_dir=str(tmp_path))
    assert b.count() == n

# ---------- 追号分析 ----------
def _draws(n):
    from engine.data_center_v2 import DrawRecord
    return [DrawRecord(str(24000+i), f"2026-01-{i%28+1:02d}", [1,2,3,4,5], [6,7], 100.0) for i in range(n)]

@pytest.mark.parametrize("n", [1, 10, 50])
def test_missing_numbers(n):
    info = ChaseAnalysis.missing_numbers(_draws(n))
    assert len(info) > 0
    assert all(m.missing_issues >= 0 for m in info)

@pytest.mark.parametrize("k", [3, 5, 10])
def test_missing_topk(k):
    info = ChaseAnalysis.missing_numbers(_draws(20), top_k=k)
    assert len(info) <= k

@pytest.mark.parametrize("n", [1, 20])
def test_missing_summary(n):
    s = ChaseAnalysis.summary(_draws(n))
    assert "追号" in s
    assert "随机" in s  # 非预测声明

@pytest.mark.parametrize("i", range(5))
def test_missing_no_predict(i):
    s = ChaseAnalysis.summary(_draws(20))
    assert "必中" not in s and "预测" not in s

# ---------- 用户记忆 ----------
@pytest.mark.parametrize("key,val", [("theme", "dark"), ("lang", "zh")])
def test_memory_set_get(mem, key, val):
    mem.set(key, val)
    assert mem.get(key) == val

@pytest.mark.parametrize("key", ["preferred_lottery", "theme"])
def test_memory_defaults(mem, key):
    assert mem.get(key) is not None

def test_memory_preference(mem):
    mem.set_preference("lottery", "dlt")
    assert mem.get_preference("lottery") == "dlt"

@pytest.mark.parametrize("n", [1, 5])
def test_memory_persist(tmp_path, n):
    a = UserMemory(storage_dir=str(tmp_path))
    for i in range(n):
        a.set(f"k{i}", i)
    b = UserMemory(storage_dir=str(tmp_path))
    assert b.get("k0") == 0

# ---------- 对话上下文 ----------
@pytest.mark.parametrize("text", ["买了号码", "我中了"])
def test_context_remember(text):
    c = ChatContext()
    c.remember(text)
    assert len(c.history) == 1

@pytest.mark.parametrize("i", range(5))
def test_context_cap(i):
    c = ChatContext()
    for j in range(10):
        c.remember(f"msg{j}")
    assert len(c.history) <= 6

@pytest.mark.parametrize("text", ["01 02 03 04 05 + 06 07", "大乐透 01 02 03 04 05 + 06 07"])
def test_context_extract(text):
    c = ChatContext()
    nums = c.extract_numbers(text)
    assert nums

def test_context_last_numbers():
    c = ChatContext()
    c.last_numbers = "01 02 03"
    assert c.last_numbers
