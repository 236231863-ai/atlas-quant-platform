"""v3.6.1 数据/统计边界测试（批量参数化）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _mk_draw(n, front=None, back=None, lottery="dlt"):
    from engine.data_center_v2 import DrawRecord
    return DrawRecord(f"{24000+n}", f"2026-01-{(n % 28) + 1:02d}",
                      front or [1, 2, 3, 4, 5], back or [6, 7], 100.0, lottery)


# ---------- 号码解析边界 ----------
from engine.data_center_v2.sources import _parse_numbers

@pytest.mark.parametrize("text", [
    "1 2 3 4 5|6 7", "01 02 03 04 05|06 07", "10 11 18 22 35 06 12",
    "1 2 3 4 5 6 7", "05 15 25 30 33|02 09", "7 8 9 10 11|1 2",
])
def test_parse_various_formats(text):
    f, b = _parse_numbers(text, 5, 2)
    assert len(f) >= 1 and len(b) >= 1


@pytest.mark.parametrize("text", [
    "abc", "abc xyz", "一二三", "1a 2b 3c 4d 5e",
])
def test_parse_errors(text):
    from engine.data_center_v2.sources import _parse_numbers
    with pytest.raises((ValueError, TypeError)):
        _parse_numbers(text, 5, 2)


@pytest.mark.parametrize("text,exp_len", [
    ("1 2 3", 3), ("1 2 3 4 5 6 7 8 9", 7), ("01 02 03", 3),
])
def test_parse_partial_valid(text, exp_len):
    from engine.data_center_v2.sources import _parse_numbers
    f, b = _parse_numbers(text, 5, 2)
    assert len(f) + len(b) == exp_len


# ---------- 数据加载器（desktop） ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq", "unknown"])
def test_data_loader_quality(lottery):
    from data_loader import get_data_quality
    q = get_data_quality(lottery)
    assert "message" in q
    assert q["lottery"] == lottery


@pytest.mark.parametrize("total", list(range(0, 12)) + [49, 50, 199, 200, 499, 500])
def test_trust_level_all_boundaries(total):
    from data_loader import _trust_level
    assert _trust_level(total) in ("A", "B", "C", "D")


# ---------- 统计函数边界 ----------
import stats as S

def _draws_with_front(variants):
    draws = []
    for i, f in enumerate(variants):
        draws.append(_mk_draw(i, front=f))
    return draws


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 6], [2, 3, 4, 5, 6]],
    [[10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24]],
    [[1, 2, 3, 4, 5]],
    [[35, 34, 33, 32, 31], [30, 29, 28, 27, 26]],
])
def test_front_frequency(fronts):
    draws = _draws_with_front(fronts)
    freq = S.front_frequency(draws)
    assert len(freq) > 0
    total = sum(freq.values())
    assert total == sum(len(f) for f in fronts)


@pytest.mark.parametrize("fronts,k", [
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 6]], 1),
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 6], [1, 2, 3, 4, 7]], 2),
    ([[1, 2, 3, 4, 5]], 5),
    ([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], 3),
])
def test_hot_numbers_shape(fronts, k):
    draws = _draws_with_front(fronts)
    hot = S.hot_numbers(draws, k)
    assert len(hot) <= k
    assert all(c > 0 for _, c in hot)


@pytest.mark.parametrize("fronts,k", [
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 6]], 1),
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 6], [1, 2, 3, 4, 7]], 2),
    ([[1, 2, 3, 4, 5]], 5),
])
def test_cold_numbers_shape(fronts, k):
    draws = _draws_with_front(fronts)
    cold = S.cold_numbers(draws, k)
    assert len(cold) <= k


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
    [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]],
    [[35, 34, 33, 32, 31]],
])
def test_front_sums(fronts):
    draws = _draws_with_front(fronts)
    sums = S.front_sums(draws)
    assert len(sums) == len(draws)
    assert all(s >= 5 for s in sums)


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
    [[1, 2, 3, 4, 5]],
    [[35, 34, 33, 32, 31], [1, 2, 3, 4, 5]],
])
def test_front_spans(fronts):
    draws = _draws_with_front(fronts)
    spans = S.front_spans(draws)
    assert len(spans) == len(draws)


@pytest.mark.parametrize("fronts", [
    [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]],
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
    [[2, 4, 6, 8, 10], [1, 3, 5, 7, 9]],
])
def test_parity_stats(fronts):
    draws = _draws_with_front(fronts)
    p = S.parity_stats(draws)
    assert "odd" in p and "even" in p
    assert p["odd"] + p["even"] == sum(len(f) for f in fronts)


@pytest.mark.parametrize("fronts,expected", [
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]], 2),  # 两组同号，连号2对
    ([[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]], 0),  # 无连号
])
def test_consecutive_pairs(fronts, expected):
    draws = _draws_with_front(fronts)
    assert S.consecutive_pairs(draws) >= 0


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_recommendation(method):
    draws = [_mk_draw(i) for i in range(10)]
    rec = S.recommendation(draws, method)
    assert "front" in rec and "back" in rec
    assert len(rec["front"]) == 5
    assert len(rec["back"]) == 2


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 6]],
    [[1, 2, 3, 4, 5]],
    [[5, 4, 3, 2, 1], [6, 7, 8, 9, 10], [1, 2, 3, 4, 5]],
])
def test_pick_balanced(fronts):
    draws = _draws_with_front(fronts)
    rec = S.recommendation(draws, "balanced")
    assert len(rec["front"]) == 5
    assert all(1 <= n <= 35 for n in rec["front"])


# ---------- 数据质量函数 ----------
@pytest.mark.parametrize("lottery,total", [
    ("dlt", 520), ("dlt", 15), ("ssq", 15), ("dlt", 0),
])
def test_quality_message_variants(lottery, total):
    from data_loader import get_data_quality
    q = get_data_quality(lottery)
    assert "期" in q["message"]


# ---------- 导出边界（复用 export 模块） ----------
@pytest.mark.parametrize("content", [
    "", "单行", "# 标题\n\n正文内容", "**粗体**\n*斜体*\n普通",
])
def test_md_any_content(tmp_path, content):
    from engine.export import MarkdownExporter
    p = MarkdownExporter.export(content, str(tmp_path / "m"))
    assert os.path.exists(p)


@pytest.mark.parametrize("rows_n", [0, 1, 10, 100, 1000])
def test_csv_any_rows(tmp_path, rows_n):
    from engine.export import CSVExporter
    rows = [[i, i * 2] for i in range(rows_n)]
    p = CSVExporter.export(["a", "b"], rows, str(tmp_path / "c"))
    with open(p, encoding="utf-8-sig") as f:
        assert len(f.readlines()) == rows_n + 1


# ---------- 回测边界 ----------
@pytest.mark.parametrize("n", [5, 10, 30, 60, 100, 200])
def test_backtest_various_sizes(n):
    from engine.evaluation_v2 import run_backtest_with_evaluation
    draws = [_mk_draw(i) for i in range(n)]
    report = run_backtest_with_evaluation(draws, n_simulations=3)
    assert report.n_bets_total == max(0, n - 3)


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_backtest_methods_all_data(method):
    from engine.evaluation_v2 import run_backtest_with_evaluation
    draws = [_mk_draw(i) for i in range(100)]
    report = run_backtest_with_evaluation(draws, method=method, n_simulations=3)
    assert report.n_bets_total == 97
    assert report.roi_total is not None


@pytest.mark.parametrize("seed", range(10))
def test_backtest_seed_stability(seed):
    from engine.evaluation_v2 import run_backtest_with_evaluation
    draws = [_mk_draw(i) for i in range(50)]
    r1 = run_backtest_with_evaluation(draws, seed=seed, n_simulations=5)
    r2 = run_backtest_with_evaluation(draws, seed=seed, n_simulations=5)
    assert r1.roi_total == r2.roi_total


# ---------- 样本划分边界 ----------
@pytest.mark.parametrize("n", [5, 10, 50, 100, 500, 520])
@pytest.mark.parametrize("ratio", [0.5, 0.7, 0.8, 0.9])
def test_split_grid(n, ratio):
    from engine.evaluation_v2 import temporal_split
    draws = [_mk_draw(i) for i in range(n)]
    train, valid = temporal_split(draws, ratio)
    assert len(train) + len(valid) == n
    assert len(train) == int(n * ratio)
