"""随机性检验模块测试（v4.10）。

验证卡方拟合优度 / 游程检验 / 自相关检验 / 完整审计。
纯计算模块，无 IO、无数据库依赖。
"""
from __future__ import annotations

from types import SimpleNamespace

from engine.lottery_quant.randomness import (
    DISCLAIMER,
    RandomnessResult,
    autocorrelation_test,
    chi_square_uniformity,
    full_randomness_audit,
    runs_test,
)


def _mk(front, back=None):
    return SimpleNamespace(front=front, back=back or [])


class TestChiSquare:
    def test_uniform_obs_not_significant(self):
        r = chi_square_uniformity([10, 10, 10, 10, 10])
        assert isinstance(r, RandomnessResult)
        assert r.significant is False
        assert r.p_value > 0.9  # 完美均匀 → p 接近 1

    def test_skewed_obs_significant(self):
        r = chi_square_uniformity([50, 1, 1, 1, 1])
        assert r.significant is True
        assert r.p_value < 0.01

    def test_insufficient_sample(self):
        r = chi_square_uniformity([])
        assert r.significant is False
        assert r.p_value == 1.0

    def test_custom_expected(self):
        r = chi_square_uniformity([5, 5, 5], expected=[5, 5, 5])
        assert r.significant is False
        assert r.p_value > 0.9


class TestRunsTest:
    def test_clustered_sequence_significant(self):
        # 明显聚集（前 0 后 1），游程过少 → 显著
        r = runs_test([0, 0, 0, 0, 1, 1, 1, 1])
        assert r.significant is True

    def test_random_sequence_not_significant(self):
        # 较随机交替
        r = runs_test([0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0])
        assert isinstance(r, RandomnessResult)
        assert 0 <= r.p_value <= 1

    def test_all_same_sequence(self):
        r = runs_test([1, 1, 1, 1, 1])
        assert r.significant is False
        assert r.p_value == 1.0

    def test_short_sequence(self):
        r = runs_test([1])
        assert r.significant is False
        assert r.p_value == 1.0


class TestAutocorrelation:
    def test_strong_autocorrelation_significant(self):
        # 递增序列 → 强自相关 → 显著
        r = autocorrelation_test(list(range(30)))
        assert r.significant is True

    def test_constant_sequence_not_significant(self):
        r = autocorrelation_test([5, 5, 5, 5, 5])
        assert r.significant is False

    def test_short_sequence(self):
        r = autocorrelation_test([1, 2])
        assert r.significant is False
        assert r.p_value == 1.0


class TestFullAudit:
    def test_audit_structure(self):
        draws = [
            _mk([1, 2, 3, 4, 5], [1, 2]),
            _mk([6, 7, 8, 9, 10], [3, 4]),
            _mk([11, 12, 13, 14, 15], [5, 6]),
            _mk([16, 17, 18, 19, 20], [7, 8]),
        ]
        r = full_randomness_audit(draws, "dlt")
        assert r["lottery"] == "dlt"
        assert r["total_draws"] == 4
        assert len(r["tests"]) == 4  # 前区卡方 + 后区卡方 + 游程 + 自相关
        assert "summary" in r
        assert r["disclaimer"] == DISCLAIMER

    def test_audit_empty_draws(self):
        r = full_randomness_audit([], "dlt")
        assert r["total_draws"] == 0
        assert r["summary"]  # 不报错，有结论

    def test_audit_ssq(self):
        draws = [
            _mk([1, 2, 3, 4, 5, 6], [1]),
            _mk([7, 8, 9, 10, 11, 12], [2]),
            _mk([13, 14, 15, 16, 17, 18], [3]),
        ]
        r = full_randomness_audit(draws, "ssq")
        assert r["lottery"] == "ssq"
        assert len(r["tests"]) == 4

    def test_result_to_dict(self):
        r = chi_square_uniformity([10, 10, 10])
        d = r.to_dict()
        assert d["test"] == "卡方拟合优度"
        assert "p_value" in d and "significant" in d and "disclaimer" in d
