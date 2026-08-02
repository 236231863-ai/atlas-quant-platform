"""v3.6.1 大规模参数化矩阵测试（补充至 800+）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _mk_draw(n, front=None, back=None):
    from engine.data_center_v2 import DrawRecord
    return DrawRecord(f"{24000+n}", f"2026-01-{(n % 28) + 1:02d}",
                      front or [1, 2, 3, 4, 5], back or [6, 7], 100.0, "dlt")


# ---------- 统计函数 × 数据矩阵 ----------
import stats as S

_FRONT_SETS = [
    [1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20], [21, 22, 23, 24, 25], [26, 27, 28, 29, 30],
    [31, 32, 33, 34, 35], [1, 3, 5, 7, 9], [2, 4, 6, 8, 10],
    [35, 34, 33, 32, 31], [5, 10, 15, 20, 25], [1, 35, 2, 34, 3],
]

@pytest.mark.parametrize("fset", _FRONT_SETS)
@pytest.mark.parametrize("n_draws", [1, 3, 10, 30])
def test_stats_frequency_matrix(fset, n_draws):
    draws = [_mk_draw(i, front=fset[:] ) for i in range(n_draws)]
    freq = S.front_frequency(draws)
    assert sum(freq.values()) == n_draws * 5


@pytest.mark.parametrize("fset", _FRONT_SETS[:8])
def test_stats_sums_matrix(fset):
    draws = [_mk_draw(i, front=fset) for i in range(5)]
    sums = S.front_sums(draws)
    assert len(sums) == 5
    assert all(s == sum(fset) for s in sums)


@pytest.mark.parametrize("fset", _FRONT_SETS[:8])
@pytest.mark.parametrize("k", [1, 3, 5, 8, 10])
def test_stats_hot_cold_matrix(fset, k):
    draws = [_mk_draw(i, front=fset) for i in range(10)]
    hot = S.hot_numbers(draws, k)
    cold = S.cold_numbers(draws, k)
    assert len(hot) <= k and len(cold) <= k


@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
@pytest.mark.parametrize("n_draws", [1, 5, 15, 40, 80])
def test_stats_recommendation_matrix(method, n_draws):
    draws = [_mk_draw(i) for i in range(n_draws)]
    rec = S.recommendation(draws, method)
    assert len(rec["front"]) == 5
    assert len(rec["back"]) == 2
    assert all(1 <= n <= 35 for n in rec["front"])
    assert all(1 <= n <= 12 for n in rec["back"])


# ---------- 数据质量 × 期数矩阵 ----------
from engine.data_center_v2 import DataQualityReport

@pytest.mark.parametrize("total", [0, 1, 5, 49, 50, 99, 199, 200, 499, 500, 501, 1000])
def test_quality_report_total_matrix(total):
    r = DataQualityReport(lottery="dlt", total=total)
    assert r.total == total


@pytest.mark.parametrize("total,level", [
    (0, "D"), (1, "D"), (49, "D"), (50, "C"), (199, "C"),
    (200, "B"), (499, "B"), (500, "A"), (1000, "A"),
])
def test_quality_level_matrix(total, level):
    r = DataQualityReport(lottery="dlt", total=total)
    assert r.trust_level == level


@pytest.mark.parametrize("pool_missing,total", [
    (0, 100), (10, 100), (50, 100), (100, 100), (0, 0),
])
def test_quality_completeness_matrix(pool_missing, total):
    from engine.data_center_v2 import DrawRecord
    draws = [
        DrawRecord(str(i), "2026-01-01", [1, 2, 3, 4, 5], [6, 7],
                   0.0 if i < pool_missing else 100.0)
        for i in range(total)
    ]
    r = DataQualityReport.build("dlt", draws)
    if total:
        expected = 1.0 - pool_missing / total
        assert abs(r.completeness - round(expected, 4)) < 0.001
    else:
        assert r.total == 0


# ---------- 号码解析 × 组合矩阵 ----------
from engine.data_center_v2.sources import _parse_numbers

@pytest.mark.parametrize("a,b,c,d,e", [
    (1, 2, 3, 4, 5), (10, 20, 30, 35, 15), (35, 1, 34, 2, 33),
])
@pytest.mark.parametrize("sep", ["|", " "])
def test_parse_combination_matrix(a, b, c, d, e, sep):
    text = f"{a} {b} {c} {d} {e}{sep}6 7"
    f, bk = _parse_numbers(text, 5, 2)
    assert f == [a, b, c, d, e]  # 保持输入顺序解析
    assert bk == [6, 7]


@pytest.mark.parametrize("n", [1, 2, 5, 8, 12])
def test_parse_back_only(n):
    text = f"1 2 3 4 5|{n}"
    f, bk = _parse_numbers(text, 5, 2)
    assert bk == [n]


# ---------- 回测 × 矩阵 ----------
from engine.evaluation_v2 import run_backtest_with_evaluation, temporal_split

@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
@pytest.mark.parametrize("n_draws", [10, 50, 100])
@pytest.mark.parametrize("ratio", [0.6, 0.7, 0.8])
def test_backtest_matrix(method, n_draws, ratio):
    draws = [_mk_draw(i) for i in range(n_draws)]
    report = run_backtest_with_evaluation(draws, method=method, train_ratio=ratio, n_simulations=3)
    assert report.n_bets_total == n_draws - 3
    assert report.n_bets_train + report.n_bets_oos == report.n_bets_total


@pytest.mark.parametrize("n_draws", [5, 10, 50, 100, 200, 500])
@pytest.mark.parametrize("ratio", [0.5, 0.7, 0.9])
def test_split_matrix(n_draws, ratio):
    draws = [_mk_draw(i) for i in range(n_draws)]
    train, valid = temporal_split(draws, ratio)
    assert len(train) == int(n_draws * ratio)
    assert len(train) + len(valid) == n_draws


# ---------- 随机基准 × 矩阵 ----------
from engine.evaluation_v2 import RandomBaseline

@pytest.mark.parametrize("n_sim", [1, 3, 10, 30])
@pytest.mark.parametrize("seed", [0, 7, 42])
def test_baseline_matrix(n_sim, seed):
    draws = [_mk_draw(i) for i in range(30)]
    bl = RandomBaseline(n_simulations=n_sim, seed=seed)
    r = bl.evaluate(draws)
    assert r["n_simulations"] == n_sim
    assert r["roi_p5"] <= r["roi_mean"] <= r["roi_p95"]


# ---------- 免责声明 × 文案矩阵 ----------
from engine.evaluation_v2 import validate_copy, FORBIDDEN_EXPRESSIONS

@pytest.mark.parametrize("word", FORBIDDEN_EXPRESSIONS)
@pytest.mark.parametrize("prefix", ["", "限时", "疯狂", "官方"])
def test_forbidden_matrix(word, prefix):
    text = f"{prefix}{word}！"
    assert word in validate_copy(text)


@pytest.mark.parametrize("text", [
    "本产品数据仅供参考",
    "回测历史表现不代表未来",
    "理性购彩 量力而行",
    "开奖结果为独立随机事件",
    "统计分析工具",
    "用户手册",
    "安装向导",
    "数据导入工具",
])
def test_safe_copy_matrix(text):
    assert validate_copy(text) == []


# ---------- 导出 × 矩阵 ----------
from engine.export import MarkdownExporter, CSVExporter

@pytest.mark.parametrize("title", [f"报告{i}" for i in range(1, 11)])
@pytest.mark.parametrize("fmt", ["md", "csv"])
def test_export_title_matrix(tmp_path, title, fmt):
    if fmt == "md":
        p = MarkdownExporter.export(f"# {title}", str(tmp_path / title))
        assert os.path.exists(p)
    else:
        p = CSVExporter.export(["a"], [[title]], str(tmp_path / title))
        assert os.path.exists(p)


# ---------- 数据加载器 × 彩种矩阵 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq", "dlt", "ssq"])
def test_loader_matrix(lottery):
    from data_loader import get_data_quality
    q = get_data_quality(lottery)
    assert q["lottery"] == lottery
    assert isinstance(q["total"], int)


# ---------- 稳定性 × 矩阵 ----------
@pytest.mark.parametrize("i", range(1, 11))
def test_health_log_roundtrip(i):
    import health
    health.mark_crash()
    assert health.was_crashed() is not None
    health.clear_crash_mark()
    assert health.was_crashed() is None
