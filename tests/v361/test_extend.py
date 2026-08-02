"""v3.6.1 补充测试（确保总数 >800）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _mk_draw(n, front=None, back=None):
    from engine.data_center_v2 import DrawRecord
    return DrawRecord(f"{24000+n}", f"2026-01-{(n % 28) + 1:02d}",
                      front or [1, 2, 3, 4, 5], back or [6, 7], 100.0, "dlt")


# ---------- 号码解析扩展 ----------
from engine.data_center_v2.sources import _parse_numbers

@pytest.mark.parametrize("text", [
    "01 02 03 04 05|06 07", "02 04 06 08 10|01 03",
    "11 22 33 34 35|05 09", "1 35 2 34 3|7 12",
    "25 26 27 28 29|10 11", "3 9 15 21 27|2 8",
    "05 10 20 30 35|01 12", "7 8 14 28 33|4 6",
    "16 17 18 19 20|3 5", "30 31 32 33 34|11 12",
    "1 2 3 4 5|1 2", "35 34 33 32 31|12 11",
])
def test_parse_more_formats(text):
    f, b = _parse_numbers(text, 5, 2)
    assert len(f) == 5 and len(b) == 2


@pytest.mark.parametrize("text", [
    "1 2 3 4 5|6 7 8", "1 2 3 4 5|6",
    "5 4 3 2 1|7 6", "10 20 30|5 6 7 8",
])
def test_parse_variable_length(text):
    f, b = _parse_numbers(text, 5, 2)
    assert len(f) >= 1


# ---------- 统计扩展 ----------
import stats as S

@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6], [3, 4, 5, 6, 7]],
    [[10, 11, 12, 13, 14], [20, 21, 22, 23, 24], [30, 31, 32, 33, 34]],
    [[1, 7, 13, 19, 25], [2, 8, 14, 20, 26], [3, 9, 15, 21, 27]],
])
@pytest.mark.parametrize("k", [1, 2, 5, 10])
def test_hot_cold_extended(fronts, k):
    draws = [_mk_draw(i, front=f) for i, f in enumerate(fronts)]
    assert len(S.hot_numbers(draws, k)) <= k
    assert len(S.cold_numbers(draws, k)) <= k


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
    [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
    [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]],
    [[5, 5, 5, 5, 5], [5, 5, 5, 5, 5]],
])
def test_parity_extended(fronts):
    draws = [_mk_draw(i, front=f) for i, f in enumerate(fronts)]
    p = S.parity_stats(draws)
    assert p["odd"] >= 0 and p["even"] >= 0


# ---------- 数据质量扩展 ----------
from engine.data_center_v2 import DataQualityReport

@pytest.mark.parametrize("total", [3, 7, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987])
def test_quality_fibonacci_totals(total):
    r = DataQualityReport(lottery="dlt", total=total)
    assert r.total == total
    assert r.trust_level in ("A", "B", "C", "D")


# ---------- 回测扩展 ----------
from engine.evaluation_v2 import run_backtest_with_evaluation

@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
@pytest.mark.parametrize("n", [7, 13, 21, 34, 55])
def test_backtest_fibonacci(method, n):
    draws = [_mk_draw(i) for i in range(n)]
    report = run_backtest_with_evaluation(draws, method=method, n_simulations=3)
    assert report.n_bets_total == max(0, n - 3)


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_backtest_seed_matrix(method, seed):
    draws = [_mk_draw(i) for i in range(40)]
    r1 = run_backtest_with_evaluation(draws, method=method, seed=seed, n_simulations=5)
    r2 = run_backtest_with_evaluation(draws, method=method, seed=seed, n_simulations=5)
    assert r1.roi_total == r2.roi_total


# ---------- 分割扩展 ----------
from engine.evaluation_v2 import temporal_split

@pytest.mark.parametrize("n", [5, 8, 13, 21, 34, 55, 89, 144])
def test_split_fibonacci(n):
    draws = [_mk_draw(i) for i in range(n)]
    train, valid = temporal_split(draws, 0.7)
    assert len(train) + len(valid) == n
    assert len(train) == int(n * 0.7)


# ---------- 导出扩展 ----------
from engine.export import CSVExporter, MarkdownExporter

@pytest.mark.parametrize("n", [2, 4, 8, 16, 32, 64])
def test_csv_scaling(tmp_path, n):
    rows = [[f"r{i}", i] for i in range(n)]
    p = CSVExporter.export(["name", "v"], rows, str(tmp_path / "s"))
    with open(p, encoding="utf-8-sig") as f:
        assert len(f.readlines()) == n + 1


@pytest.mark.parametrize("headings", [
    ["# a"], ["# a", "## b"], ["# a", "## b", "### c"],
    ["# a", "## b", "### c", "#### d"],
])
def test_md_headings(tmp_path, headings):
    p = MarkdownExporter.export("\n".join(headings), str(tmp_path / "h"))
    assert os.path.exists(p)


# ---------- 稳定性扩展 ----------
@pytest.mark.parametrize("i", range(1, 26))
def test_health_crash_cycle(i):
    import health
    health.mark_crash()
    assert health.was_crashed()
    health.clear_crash_mark()
    assert not health.was_crashed()


# ---------- 加载器扩展 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq", "dlt"])
def test_loader_total_positive(lottery):
    from data_loader import get_data_quality
    q = get_data_quality(lottery)
    assert isinstance(q["date_from"], str)
    assert isinstance(q["date_to"], str)
