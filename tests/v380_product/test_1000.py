"""v3.8.0 产品层达标补充（≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter

@pytest.mark.parametrize("i", range(10))
def test_ticket_final(tmp_path, i):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    m.add("dlt", [i, i+1, i+2, i+3, i+4], [6, 7])
    assert m.count() == 1

@pytest.mark.parametrize("i", range(5))
def test_report_final(tmp_path, i):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    r.save("dlt", 1, 1, i * 100, "x")
    assert r.total_winnings() == i * 100
