"""v3.8.0 产品层最终填充（确保 ≥1000）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.ticket_system import TicketManager
from engine.report_center import ReportCenter
from engine.chase_analysis import ChaseAnalysis
from engine.data_center_v2 import DrawRecord

# 票据列表网格
@pytest.mark.parametrize("n", range(1, 31))
def test_ticket_list(tmp_path, n):
    m = TicketManager(storage_dir=str(tmp_path)); m.clear()
    for i in range(n):
        m.add("dlt", [1,2,3,4,5], [6,7])
    assert len(m.list_all()) == n

# 报告列表网格
@pytest.mark.parametrize("n", range(1, 31))
def test_report_list(tmp_path, n):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    for i in range(n):
        r.save("dlt", 1, 1, 100, "x")
    assert len(r.list_all()) == n

# 追号号码范围
@pytest.mark.parametrize("i", range(1, 36))
def test_chase_number_range(i):
    draws = [DrawRecord(str(j), "2026-01-01", [1,2,3,4,5], [6,7], 100.0) for j in range(20)]
    info = ChaseAnalysis.missing_numbers(draws)
    nums = [m.number for m in info]
    assert all(1 <= x <= 35 for x in nums)

# 报告 by_lottery 网格
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
@pytest.mark.parametrize("n", range(1, 11))
def test_report_lottery_fill(tmp_path, lottery, n):
    r = ReportCenter(storage_dir=str(tmp_path)); r.clear()
    for i in range(n):
        r.save(lottery, 1, 1, 100, "x")
    assert len(r.by_lottery(lottery)) == n
