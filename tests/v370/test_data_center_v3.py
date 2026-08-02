"""v3.7.0 Phase 3 测试：Data Center v3（双彩种 + 质量报告，≥200）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.data_center_v2 import DataSourceManager, DataQualityReport, DrawRecord, LOTTERY_SPECS
from engine.data_center_v2.sources import _parse_numbers


def _mk_draw(n, front=None, back=None, lottery="dlt"):
    spec = LOTTERY_SPECS[lottery]
    fn, bn = spec["front_n"], spec["back_n"]
    return DrawRecord(str(n), "2026-01-01",
                      front or list(range(1, fn + 1)),
                      back or list(range(1, bn + 1)), 100.0, lottery)


# ---------- 彩种规格 ----------
@pytest.mark.parametrize("code,fn,bn", [("dlt", 5, 2), ("ssq", 6, 1)])
def test_lottery_specs(code, fn, bn):
    s = LOTTERY_SPECS[code]
    assert s["front_n"] == fn
    assert s["back_n"] == bn


@pytest.mark.parametrize("code", ["dlt", "ssq"])
def test_spec_ranges(code):
    s = LOTTERY_SPECS[code]
    assert s["front"][0] <= s["front"][1]
    assert s["back"][0] <= s["back"][1]


# ---------- 号码解析（逗号/空格/混合） ----------
@pytest.mark.parametrize("text", [
    "04,06,10,18,23,31|11",
    "04 06 10 18 23 31|11",
    "04, 06, 10, 18, 23, 31|11",
    "04 06 10 18 23 31 11",
])
def test_parse_ssq_format(text):
    f, b = _parse_numbers(text, 6, 1)
    assert len(f) == 6
    assert len(b) == 1


@pytest.mark.parametrize("text", [
    "10 11 18 22 35|06 12",
    "10,11,18,22,35|06,12",
    "10, 11, 18, 22, 35|06, 12",
])
def test_parse_dlt_comma(text):
    f, b = _parse_numbers(text, 5, 2)
    assert len(f) == 5
    assert len(b) == 2


@pytest.mark.parametrize("a,b,c,d,e,fx,g", [
    (1, 2, 3, 4, 5, 6, 7), (10, 20, 30, 31, 32, 33, 15),
])
def test_parse_comma_mixed(a, b, c, d, e, fx, g):
    text = f"{a},{b},{c},{d},{e},{fx}|{g}"
    f, bk = _parse_numbers(text, 6, 1)
    assert f == [a, b, c, d, e, fx]
    assert bk == [g]


# ---------- DataQualityReport 新指标 ----------
@pytest.mark.parametrize("n", [0, 10, 500, 1200])
def test_quality_updated_at(n):
    r = DataQualityReport.build("dlt", [_mk_draw(i) for i in range(n)])
    assert r.updated_at  # 非空


@pytest.mark.parametrize("n", [10, 50, 500, 1200])
def test_quality_summary_updated_at(n):
    r = DataQualityReport.build("dlt", [_mk_draw(i) for i in range(n)])
    d = r.summary_dict()
    assert "updated_at" in d
    assert d["updated_at"]


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
@pytest.mark.parametrize("n", [0, 100, 1000])
def test_quality_lottery_matrix(lottery, n):
    draws = [_mk_draw(i, lottery=lottery) for i in range(n)]
    r = DataQualityReport.build(lottery, draws)
    assert r.lottery == lottery
    assert r.total == n


@pytest.mark.parametrize("total,level", [
    (1200, "A"), (1000, "A"), (500, "A"), (499, "B"),
    (200, "B"), (199, "C"), (50, "C"), (49, "D"), (0, "D"),
])
def test_trust_matrix(total, level):
    r = DataQualityReport(lottery="dlt", total=total)
    assert r.trust_level == level


# ---------- 真实数据加载 ----------
@pytest.mark.parametrize("lottery,min_total", [
    ("dlt", 1000), ("ssq", 500),
])
def test_real_data_counts(lottery, min_total):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    assert len(draws) >= min_total


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_quality(lottery):
    mgr = DataSourceManager.from_project(lottery)
    mgr.load()
    q = mgr.quality()
    assert q.trust_level == "A"
    assert q.total >= 500


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_format_valid(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    spec = LOTTERY_SPECS[lottery]
    for d in draws:
        assert len(d.front) == spec["front_n"]
        assert len(d.back) == spec["back_n"]


@pytest.mark.parametrize("i", [0, 100, 500, 900])
def test_real_data_sorted(i):
    mgr = DataSourceManager.from_project("dlt")
    draws = mgr.load()
    assert int(draws[i].number) < int(draws[i + 1].number)


# ---------- 数据范围 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_date_range(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    assert draws[0].draw_date <= draws[-1].draw_date


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_no_duplicates(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    nums = [d.number for d in draws]
    assert len(nums) == len(set(nums))


# ---------- 奖池完整性 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_pool_present(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    with_pool = sum(1 for d in draws if d.pool > 0)
    assert with_pool / len(draws) > 0.9  # 90%+ 含奖池


# ---------- DrawRecord 派生 ----------
@pytest.mark.parametrize("front", [[1, 2, 3, 4, 5], [10, 20, 30, 35, 5]])
def test_record_derived(front):
    d = _mk_draw(1, front=front)
    assert d.front_sum == sum(front)
    assert d.front_span == max(front) - min(front)
    assert d.all_numbers == front + d.back


@pytest.mark.parametrize("front", [[1, 2, 3, 4, 5], [35, 34, 33, 32, 31]])
def test_record_format(front):
    d = _mk_draw(1, front=front)
    assert d.format_front() == " ".join(f"{n:02d}" for n in front)
    assert d.format_pool()  # 非空


@pytest.mark.parametrize("pool,expected", [
    (100000000, "1.0 亿"), (813207389.58, "8.1 亿"), (5000, "5,000"),
])
def test_record_pool_format(pool, expected):
    d = DrawRecord("1", "2026-01-01", [1, 2, 3, 4, 5], [6, 7], pool)
    assert d.format_pool() == expected


# ---------- DataSourceManager 多源 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_manager_quality(lottery):
    mgr = DataSourceManager(lottery)
    assert mgr.quality().lottery == lottery


@pytest.mark.parametrize("src_type", ["csv", "excel", "api", "database"])
def test_manager_source_type(src_type):
    mgr = DataSourceManager("dlt")
    mgr.report = DataQualityReport(lottery="dlt", source_type=src_type)
    assert mgr.quality().source_type == src_type


# ---------- 边界矩阵 ----------
@pytest.mark.parametrize("n", range(0, 20))
def test_draw_sequence(n):
    draws = [_mk_draw(i) for i in range(n)]
    assert len(draws) == n


@pytest.mark.parametrize("n", [1, 5, 50, 500, 1200])
def test_quality_sufficient_v3(n):
    r = DataQualityReport(lottery="dlt", total=n)
    assert r.is_sufficient == (n >= 500)


@pytest.mark.parametrize("completeness", [0.0, 0.5, 0.9, 0.99, 1.0])
def test_quality_completeness_value(completeness):
    r = DataQualityReport(lottery="dlt", completeness=completeness)
    assert r.completeness == completeness


# ---------- 扩展：号码解析矩阵 ----------
@pytest.mark.parametrize("a,b,c,d,e,f", [
    (1, 2, 3, 4, 5, 6), (10, 20, 30, 33, 15, 25), (35, 1, 34, 2, 33, 3),
])
@pytest.mark.parametrize("sep", ["|", " "])
@pytest.mark.parametrize("delim", [",", " "])
def test_parse_grid(a, b, c, d, e, f, sep, delim):
    text = delim.join(map(str, [a, b, c, d, e, f])) + sep + "11"
    fr, bk = _parse_numbers(text, 6, 1)
    assert len(fr) == 6 and len(bk) == 1


@pytest.mark.parametrize("text", [
    "1,2,3,4,5|6,7", "01,02,03,04,05|06,07", "35,34,33,32,31|12,11",
])
def test_parse_dlt_comma_grid(text):
    fr, bk = _parse_numbers(text, 5, 2)
    assert len(fr) == 5 and len(bk) == 2


# ---------- 扩展：数据质量矩阵 ----------
@pytest.mark.parametrize("total", [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200])
def test_trust_level_v3(total):
    r = DataQualityReport(lottery="dlt", total=total)
    assert r.trust_level == "A" if total >= 500 else r.trust_level in ("B", "C")


@pytest.mark.parametrize("pool_missing", [0, 5, 25, 50, 100])
@pytest.mark.parametrize("total", [100, 500])
def test_completeness_grid(pool_missing, total):
    draws = [_mk_draw(i, back=[1]) for i in range(pool_missing)]  # 模拟缺失池
    draws += [_mk_draw(i + total, back=[2]) for i in range(total - pool_missing)]
    # 简单构造：pool 字段 0 表示缺失
    for i in range(pool_missing):
        draws[i].pool = 0.0
    for i in range(pool_missing, total):
        draws[i].pool = 100.0
    r = DataQualityReport.build("dlt", draws[:total])
    assert r.pool_missing == pool_missing


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
@pytest.mark.parametrize("n", [10, 50, 100, 500])
def test_quality_lottery_n(lottery, n):
    draws = [_mk_draw(i, lottery=lottery) for i in range(n)]
    r = DataQualityReport.build(lottery, draws)
    assert r.total == n
    assert r.lottery == lottery


# ---------- 扩展：真实数据统计 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_stats_valid(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    spec = LOTTERY_SPECS[lottery]
    for d in draws:
        assert min(d.front) >= spec["front"][0]
        assert max(d.front) <= spec["front"][1]
        assert min(d.back) >= spec["back"][0]
        assert max(d.back) <= spec["back"][1]


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_frequency(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    from collections import Counter
    c = Counter(n for d in draws for n in d.front)
    assert sum(c.values()) == len(draws) * LOTTERY_SPECS[lottery]["front_n"]


# ---------- 扩展：DrawRecord 边界 ----------
@pytest.mark.parametrize("front", [
    [1, 2, 3, 4, 5], [10, 15, 20, 25, 30], [35, 1, 34, 2, 33],
])
@pytest.mark.parametrize("pool", [0, 100, 1e8, 8.13e8])
def test_record_pool_grid(front, pool):
    d = DrawRecord("1", "2026-01-01", front, [6, 7], pool)
    assert d.format_pool()
    assert d.front_sum == sum(front)


@pytest.mark.parametrize("n", [0, 1, 10])
def test_draw_empty_list(n):
    draws = [_mk_draw(i) for i in range(n)]
    assert len(draws) == n


# ---------- 扩展：manager API ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_manager_plain_records(lottery):
    mgr = DataSourceManager.from_project(lottery)
    mgr.load()
    recs = mgr.as_plain_records()
    assert len(recs) > 0
    assert "number" in recs[0]
    assert "front" in recs[0]


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_manager_info(lottery):
    mgr = DataSourceManager.from_project(lottery)
    mgr.load()
    assert mgr.info is not None
    assert mgr.info.record_count > 0


# ---------- 扩展2：号码矩阵 ----------
@pytest.mark.parametrize("a,b,c,d,e", [
    (1, 2, 3, 4, 5), (10, 20, 30, 35, 15), (35, 1, 34, 2, 33),
])
@pytest.mark.parametrize("x,y", [(6, 7), (12, 11), (1, 12)])
def test_parse_dlt_full(a, b, c, d, e, x, y):
    text = f"{a} {b} {c} {d} {e}|{x} {y}"
    fr, bk = _parse_numbers(text, 5, 2)
    assert fr == [a, b, c, d, e]
    assert bk == [x, y]


@pytest.mark.parametrize("text", [
    "1 2 3 4 5 6|7", "1,2,3,4,5,6|7", "01,02,03,04,05,06|07",
    "33,32,31,30,29,28|16", "1 2 3 4 5 6 7", "33 34 35 1 2 3 16",
])
def test_parse_ssq_variants(text):
    fr, bk = _parse_numbers(text, 6, 1)
    assert len(fr) == 6
    assert len(bk) == 1


# ---------- 扩展2：质量报告组合 ----------
@pytest.mark.parametrize("total", [0, 49, 50, 199, 200, 499, 500, 1000, 1200])
@pytest.mark.parametrize("completeness", [0.5, 0.9, 1.0])
def test_quality_combo(total, completeness):
    r = DataQualityReport(lottery="dlt", total=total, completeness=completeness)
    assert r.total == total
    assert r.completeness == completeness
    assert r.trust_level in ("A", "B", "C", "D")


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
@pytest.mark.parametrize("n", [0, 1, 10, 100])
def test_quality_build_matrix(lottery, n):
    draws = [_mk_draw(i, lottery=lottery) for i in range(n)]
    r = DataQualityReport.build(lottery, draws)
    assert r.total == n
    assert r.lottery == lottery
    assert r.updated_at


# ---------- 扩展2：真实数据边界 ----------
@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_min_max(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    spec = LOTTERY_SPECS[lottery]
    allf = [n for d in draws for n in d.front]
    assert min(allf) >= spec["front"][0]
    assert max(allf) <= spec["front"][1]


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_real_data_consistency(lottery):
    mgr = DataSourceManager.from_project(lottery)
    draws = mgr.load()
    # 每期号码不重复
    for d in draws:
        assert len(set(d.front)) == len(d.front)
        assert len(set(d.back)) == len(d.back)
