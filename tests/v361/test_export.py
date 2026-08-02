"""v3.6.1 输出系统测试：Markdown / CSV / PNG / PDF 导出。"""
import os

import pytest

from engine.export import MarkdownExporter, CSVExporter, PNGExporter, PDFExporter
from engine.evaluation_v2 import run_backtest_with_evaluation
from engine.data_center_v2 import DrawRecord


def _mk_draws(n):
    return [
        DrawRecord(f"{24000+i}", f"2026-01-{i % 28 + 1:02d}", [1, 2, 3, 4, 5], [6, 7], 100.0)
        for i in range(n)
    ]


def _mk_records(n):
    return run_backtest_with_evaluation(_mk_draws(n), n_simulations=3).records


# ---------- Markdown ----------
@pytest.mark.parametrize("name", ["报告", "r1", "test_report", "报告2026"])
def test_md_export(tmp_path, name):
    p = MarkdownExporter.export("# 标题\n内容", str(tmp_path / name))
    assert p.endswith(".md")
    assert os.path.exists(p)
    with open(p, encoding="utf-8") as f:
        assert "标题" in f.read()


@pytest.mark.parametrize("n_sections", [0, 1, 3, 5])
def test_md_from_sections(tmp_path, n_sections):
    sections = [(f"节{i}", [f"行{j}" for j in range(3)]) for i in range(n_sections)]
    p = MarkdownExporter.from_sections("文档", sections, str(tmp_path / "doc"))
    with open(p, encoding="utf-8") as f:
        content = f.read()
    for i in range(n_sections):
        assert f"节{i}" in content


# ---------- CSV ----------
@pytest.mark.parametrize("headers,rows", [
    (["a", "b"], [[1, 2], [3, 4]]),
    (["x"], [["y"]]),
    (["期号", "号码"], [["26086", "01 02"], ["26085", "03 04"]]),
])
def test_csv_export(tmp_path, headers, rows):
    p = CSVExporter.export(headers, rows, str(tmp_path / "data"))
    assert p.endswith(".csv")
    assert os.path.exists(p)


@pytest.mark.parametrize("n_records", [1, 5, 20, 50, 100])
def test_csv_export_records(tmp_path, n_records):
    records = _mk_records(n_records + 3)
    p = CSVExporter.export_records(records, str(tmp_path / "bt"))
    with open(p, encoding="utf-8-sig") as f:
        lines = f.readlines()
    assert len(lines) == len(records) + 1  # + 表头


@pytest.mark.parametrize("has_win", [True, False])
def test_csv_records_win_column(tmp_path, has_win):
    records = _mk_records(10)
    p = CSVExporter.export_records(records, str(tmp_path / "bt2"))
    content = open(p, encoding="utf-8-sig").read()
    assert "期号" in content


# ---------- PNG ----------
@pytest.mark.parametrize("dpi", [80, 100, 150, 300])
def test_png_export(tmp_path, dpi):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    fig = Figure(figsize=(4, 3))
    ax = fig.add_subplot(111)
    ax.plot([1, 2, 3], [4, 5, 6])
    p = PNGExporter.export_figure(fig, str(tmp_path / "chart"), dpi=dpi)
    assert p.endswith(".png")
    assert os.path.getsize(p) > 1000


@pytest.mark.parametrize("name", ["曲线", "c1", "图 表"])
def test_png_export_custom_name(tmp_path, name):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.bar([1, 2], [3, 4])
    p = PNGExporter.export_figure(fig, str(tmp_path / name))
    assert os.path.exists(p)


# ---------- PDF ----------
@pytest.mark.parametrize("lines", [
    ["一行"],
    ["第一行", "第二行", "第三行"],
    ["**加粗**", "普通", "**又粗**"],
    [f"第{i}行" for i in range(20)],
])
def test_pdf_report_export(tmp_path, lines):
    p = PDFExporter.export_report("测试报告", lines, str(tmp_path / "report"))
    assert p.endswith(".pdf")
    assert os.path.getsize(p) > 500


@pytest.mark.parametrize("n_records", [5, 30, 100])
def test_pdf_backtest_export(tmp_path, n_records):
    records = _mk_records(n_records + 3)
    p = PDFExporter.export_backtest(records, ["摘要1", "摘要2"], str(tmp_path / "bt"))
    assert p.endswith(".pdf")
    assert os.path.getsize(p) > 500


@pytest.mark.parametrize("title", ["报告A", "Atlas Report", "回测 2026"])
def test_pdf_title_variants(tmp_path, title):
    p = PDFExporter.export_report(title, ["内容"], str(tmp_path / "t"))
    assert os.path.exists(p)


# ---------- 输出目录自动创建 ----------
@pytest.mark.parametrize("fmt_fn", [
    lambda p: MarkdownExporter.export("# x", p),
    lambda p: CSVExporter.export(["a"], [[1]], p),
])
def test_export_creates_dirs(tmp_path, fmt_fn):
    p = str(tmp_path / "a" / "b" / "c")
    out = fmt_fn(p)
    assert os.path.exists(out)
