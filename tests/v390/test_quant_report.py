"""v3.9.0 Phase 8：量化报告系统测试。"""
from __future__ import annotations

import os

import pytest

from engine.lottery_quant.report import QuantReportGenerator, generate_quant_report
from engine.lottery_quant.report.generator import DISCLAIMER

TICKETS = [
    {"front": [10, 11, 18, 22, 35], "back": [6, 12]},
    {"front": [1, 2, 3, 4, 5], "back": [6, 7]},
    {"front": [5, 10, 15, 20, 25], "back": [8, 9]},
]


@pytest.fixture()
def gen():
    return QuantReportGenerator(TICKETS, sim_trials=1000)


# ---------- Markdown 内容 ----------
def test_markdown_has_title(gen):
    assert "量化分析报告" in gen.to_markdown()


def test_markdown_has_disclaimer(gen):
    assert "不能预测未来开奖" in gen.to_markdown()


@pytest.mark.parametrize("section", [
    "免责声明", "组合评分", "概率模型", "蒙特卡洛模拟", "组合分析", "资金风险", "策略回测", "汇总",
])
def test_markdown_sections(gen, section):
    assert section in gen.to_markdown()


@pytest.mark.parametrize("kw", ["评分", "一等奖概率", "覆盖率", "重复率", "年度投入", "风险等级", "ROI"])
def test_markdown_keywords(gen, kw):
    assert kw in gen.to_markdown()


def test_markdown_no_prediction(gen):
    for banned in ("预测中奖", "提高中奖概率", "稳赚"):
        assert banned not in gen.to_markdown()


def test_markdown_lottery_name(gen):
    assert "大乐透" in gen.to_markdown()


def test_markdown_ssq():
    gen = QuantReportGenerator([{"front": [1, 2, 3, 4, 5, 6], "back": [1]}],
                               "ssq", sim_trials=1000)
    assert "双色球" in gen.to_markdown()


# ---------- 免责声明 ----------
def test_disclaimer_text():
    assert "不能预测未来开奖" in DISCLAIMER
    assert "随机性" in DISCLAIMER


@pytest.mark.parametrize("i", range(5))
def test_markdown_disclaimer_present_every_time(i):
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    assert DISCLAIMER.split("。")[0] in gen.to_markdown()


# ---------- MD 导出 ----------
def test_export_markdown(tmp_path):
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    p = gen.export_markdown(str(tmp_path / "report.md"))
    assert os.path.exists(p)
    assert p.endswith(".md")
    with open(p, encoding="utf-8") as f:
        assert "免责声明" in f.read()


def test_export_markdown_adds_ext(tmp_path):
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    p = gen.export_markdown(str(tmp_path / "report"))
    assert p.endswith(".md")


@pytest.mark.parametrize("i", range(5))
def test_export_markdown_multiple(tmp_path, i):
    p = QuantReportGenerator(TICKETS, sim_trials=1000).export_markdown(str(tmp_path / f"r{i}"))
    assert os.path.exists(p)


# ---------- PDF 导出 ----------
def test_export_pdf(tmp_path):
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    p = gen.export_pdf(str(tmp_path / "report.pdf"))
    assert os.path.exists(p)
    assert p.endswith(".pdf")
    assert os.path.getsize(p) > 1000


def test_export_pdf_adds_ext(tmp_path):
    p = QuantReportGenerator(TICKETS, sim_trials=1000).export_pdf(str(tmp_path / "r"))
    assert p.endswith(".pdf")


# ---------- PNG 导出 ----------
def test_export_png(tmp_path):
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    p = gen.export_png(str(tmp_path / "report.png"))
    assert os.path.exists(p)
    assert p.endswith(".png")
    assert os.path.getsize(p) > 1000


def test_export_png_adds_ext(tmp_path):
    p = QuantReportGenerator(TICKETS, sim_trials=1000).export_png(str(tmp_path / "chart"))
    assert p.endswith(".png")


# ---------- 便捷函数 ----------
def test_generate_md(tmp_path):
    p = generate_quant_report(TICKETS, fmt="md", path=str(tmp_path / "q.md"))
    assert os.path.exists(p)


def test_generate_pdf(tmp_path):
    p = generate_quant_report(TICKETS, fmt="pdf", path=str(tmp_path / "q.pdf"))
    assert os.path.exists(p)


def test_generate_png(tmp_path):
    p = generate_quant_report(TICKETS, fmt="png", path=str(tmp_path / "q.png"))
    assert os.path.exists(p)


def test_generate_default_path(tmp_path, monkeypatch):
    import engine.lottery_quant.report.generator as genmod
    monkeypatch.chdir(tmp_path)
    p = generate_quant_report(TICKETS, fmt="md")
    assert os.path.exists(p)


# ---------- 数据字段 ----------
def test_generator_collect_fields():
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    d = gen._collect()
    for k in ("full", "structure", "prob", "sim", "portfolio", "risk", "backtest"):
        assert k in d


def test_collect_cached():
    gen = QuantReportGenerator(TICKETS, sim_trials=1000)
    d1 = gen._collect()
    d2 = gen._collect()
    assert d1 is d2


# ---------- 参数化扩展 ----------
@pytest.mark.parametrize("seed", range(20))
def test_report_matrix(seed, tmp_path):
    import random
    rng = random.Random(seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    gen = QuantReportGenerator(tickets, sim_trials=800)
    md = gen.to_markdown()
    assert "免责声明" in md
    assert "随机性" in md
    p = gen.export_markdown(str(tmp_path / f"m{seed}"))
    assert os.path.exists(p)


@pytest.mark.parametrize("i", range(10))
def test_pdf_matrix(i, tmp_path):
    p = generate_quant_report(TICKETS, fmt="pdf", path=str(tmp_path / f"p{i}"))
    assert os.path.getsize(p) > 1000


@pytest.mark.parametrize("i", range(10))
def test_png_matrix(i, tmp_path):
    p = generate_quant_report(TICKETS, fmt="png", path=str(tmp_path / f"img{i}"))
    assert os.path.getsize(p) > 500
