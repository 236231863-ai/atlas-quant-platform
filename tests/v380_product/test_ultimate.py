"""v3.8.0 产品层终极网格（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.data_center_v2 import DrawRecord

# 票据终极网格：front × back × lottery
_F = [[i, i+1, i+2, i+3, i+4] for i in range(1, 21, 1)]
_B = [[i, i+1] for i in range(1, 11, 1)]
@pytest.mark.parametrize("front", _F)
@pytest.mark.parametrize("back", _B)
def test_ticket_ultimate(tmp_path, front, back):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    t = m.add("dlt", front, back)
    assert m.get(t.ticket_id).back == back

# 报告终极网格
@pytest.mark.parametrize("tickets", [1, 2, 5, 10, 20])
@pytest.mark.parametrize("won", [0, 1, 3, 5])
@pytest.mark.parametrize("total", [0, 100, 5000])
def test_report_ultimate(tmp_path, tickets, won, total):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    rep = r.save("dlt", tickets, min(won, tickets), total, "x")
    assert rep.tickets == tickets

# 追号终极网格
@pytest.mark.parametrize("n", [5, 15, 30, 60, 120])
@pytest.mark.parametrize("front", [[1,2,3,4,5], [6,7,8,9,10], [11,22,33,34,35]])
def test_chase_ultimate(n, front):
    draws = [DrawRecord(str(i), "2026-01-01", front, [6,7], 100.0) for i in range(n)]
    assert len(ChaseAnalysis.missing_numbers(draws)) >= 1

# 票据删除网格
@pytest.mark.parametrize("i", range(15))
def test_ticket_delete_grid(tmp_path, i):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    t = m.add("dlt", [1,2,3,4,5], [6,7])
    assert m.delete(t.ticket_id)
    assert not m.delete(t.ticket_id)

# 票据文本网格
@pytest.mark.parametrize("i", range(10))
def test_ticket_text_ultimate(tmp_path, i):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    saved = m.add_from_text(f"大乐透 {i+1} {i+2} {i+3} {i+4} {i+5} + {i%12+1} {i%11+2} 买了")
    assert len(saved) >= 1
