"""v4.0.0 Phase 4：智能报告升级（个人视角）测试。"""
from __future__ import annotations

import os
import random

import pytest

from engine.lottery_quant.report import QuantReportGenerator, generate_quant_report
from engine.lottery_quant.report.generator import DISCLAIMER

TICKETS = [
    {"front": [10, 11, 18, 22, 35], "back": [6, 12], "buy_date": "2026-07-31", "cost": 2.0},
    {"front": [1, 2, 3, 4, 5], "back": [6, 7], "buy_date": "2026-07-20", "cost": 2.0},
    {"front": [5, 10, 15, 20, 25], "back": [8, 9], "buy_date": "2026-06-15", "cost": 4.0},
]


@pytest.fixture()
def gen():
    return QuantReportGenerator(TICKETS, sim_trials=1000)


# ---------- 5 部分结构 ----------
@pytest.mark.parametrize("section", [
    "号码分析", "概率分析", "资金风险", "个人行为", "改进建议",
])
def test_five_sections(gen, section):
    assert section in gen.to_markdown()


def test_has_disclaimer(gen):
    assert "不能预测未来开奖" in gen.to_markdown()


def test_has_combination_score(gen):
    assert "组合评分" in gen.to_markdown()


def test_has_behavior_section_content(gen):
    md = gen.to_markdown()
    assert "投注期数" in md
    assert "行为风险等级" in md


def test_has_improvements(gen):
    md = gen.to_markdown()
    assert any("调整" in line or "建议" in line for line in md.splitlines())


# ---------- 改进建议替代推荐号码 ----------
def test_no_recommend_numbers(gen):
    md = gen.to_markdown()
    assert "推荐号码" not in md
    assert "推荐一注" not in md


def test_structure_adjustment(gen):
    md = gen.to_markdown()
    assert any("结构调整" in line or "组合结构" in line for line in md.splitlines())


def test_improvement_no_prediction(gen):
    md = gen.to_markdown()
    for banned in ("预测中奖", "提高中奖概率", "稳赚"):
        assert banned not in md


@pytest.mark.parametrize("i", range(10))
def test_improvements_always_present(i):
    rng = random.Random(i)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(5)]
    gen = QuantReportGenerator(tickets, sim_trials=800)
    md = gen.to_markdown()
    assert "改进建议" in md
    assert "推荐号码" not in md


# ---------- 个人行为内容 ----------
def test_behavior_tickets_count(gen):
    md = gen.to_markdown()
    assert "3 期" in md  # 3 张票据


def test_behavior_risk_level(gen):
    md = gen.to_markdown()
    assert "行为风险等级" in md


@pytest.mark.parametrize("seed", range(20))
def test_behavior_varied(seed):
    rng = random.Random(100 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(rng.randint(1, 10))]
    gen = QuantReportGenerator(tickets, sim_trials=800)
    md = gen.to_markdown()
    assert "个人行为" in md
    assert "追号次数" in md


# ---------- 概率/号码部分保留 ----------
def test_probability_content(gen):
    md = gen.to_markdown()
    assert "一等奖概率" in md
    assert "21,425,712" in md


def test_number_analysis_content(gen):
    md = gen.to_markdown()
    assert "奇偶比" in md
    assert "和值" in md


def test_risk_content(gen):
    md = gen.to_markdown()
    assert "年度投入" in md
    assert "风险等级" in md


# ---------- 免责声明 ----------
def test_disclaimer_text():
    assert "不能预测未来开奖" in DISCLAIMER
    assert "随机性" in DISCLAIMER


def test_summary_disclaimer(gen):
    md = gen.to_markdown()
    assert "随机性" in md


# ---------- 导出兼容 ----------
def test_export_md(tmp_path, gen):
    p = gen.export_markdown(str(tmp_path / "r.md"))
    assert os.path.exists(p)
    with open(p, encoding="utf-8") as f:
        assert "个人行为" in f.read()


def test_export_pdf(tmp_path, gen):
    p = gen.export_pdf(str(tmp_path / "r.pdf"))
    assert os.path.exists(p)
    assert os.path.getsize(p) > 1000


def test_export_png(tmp_path, gen):
    p = gen.export_png(str(tmp_path / "r.png"))
    assert os.path.exists(p)


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_report_matrix(seed, tmp_path):
    rng = random.Random(1000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(rng.randint(2, 8))]
    gen = QuantReportGenerator(tickets, sim_trials=800)
    md = gen.to_markdown()
    for sec in ("号码分析", "概率分析", "资金风险", "个人行为", "改进建议"):
        assert sec in md
    p = gen.export_markdown(str(tmp_path / f"r{seed}"))
    assert os.path.exists(p)


@pytest.mark.parametrize("seed", range(25))
def test_pdf_matrix(seed, tmp_path):
    p = generate_quant_report(TICKETS, fmt="pdf", path=str(tmp_path / f"p{seed}"))
    assert os.path.getsize(p) > 1000


@pytest.mark.parametrize("seed", range(25))
def test_png_matrix(seed, tmp_path):
    p = generate_quant_report(TICKETS, fmt="png", path=str(tmp_path / f"img{seed}"))
    assert os.path.getsize(p) > 500


@pytest.mark.parametrize("seed", range(30))
def test_improvement_content_matrix(seed):
    rng = random.Random(3000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(rng.randint(1, 6))]
    gen = QuantReportGenerator(tickets, sim_trials=800)
    md = gen.to_markdown()
    tips = [l for l in md.splitlines() if l.startswith("- ") and ("调整" in l or "建议" in l or "分散" in l or "保持" in l)]
    assert len(tips) >= 1
    assert "不改变中奖概率" in md


# ---------- 补充矩阵（快） ----------
@pytest.mark.parametrize("seed", range(40))
def test_improvement_variants(seed):
    rng = random.Random(5000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(rng.randint(1, 6))]
    gen = QuantReportGenerator(tickets, sim_trials=500)
    md = gen.to_markdown()
    assert "改进建议" in md
    assert "不改变中奖概率" in md
    assert "推荐号码" not in md


@pytest.mark.parametrize("seed", range(30))
def test_behavior_present_matrix(seed):
    rng = random.Random(6000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2)),
                "buy_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "cost": 2.0} for _ in range(rng.randint(2, 8))]
    gen = QuantReportGenerator(tickets, sim_trials=500)
    md = gen.to_markdown()
    assert "个人行为" in md
    assert "投注期数" in md
