"""Tests for number validation across lottery types."""
from __future__ import annotations

import pytest

from core.types import NumberRange, LotteryTypeDef


class TestNumberRange:
    def test_valid_range(self) -> None:
        r = NumberRange(min_value=1, max_value=33, count=6)
        assert r.min_value == 1
        assert r.max_value == 33
        assert r.count == 6

    def test_invalid_range_min_equals_max(self) -> None:
        with pytest.raises(ValueError, match="must be <"):
            NumberRange(min_value=5, max_value=5, count=1)

    def test_invalid_range_min_greater_than_max(self) -> None:
        with pytest.raises(ValueError, match="must be <"):
            NumberRange(min_value=10, max_value=5, count=1)

    def test_invalid_count_zero(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            NumberRange(min_value=1, max_value=33, count=0)

    def test_invalid_count_negative(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            NumberRange(min_value=1, max_value=33, count=-1)

    def test_count_exceeds_range(self) -> None:
        with pytest.raises(ValueError, match="exceeds range"):
            NumberRange(min_value=1, max_value=3, count=5)

    def test_frozen_instance(self) -> None:
        r = NumberRange(min_value=1, max_value=33, count=6)
        with pytest.raises(Exception):
            r.min_value = 99


class TestLotteryTypeDef:
    def test_create_lottery_type(self) -> None:
        lt = LotteryTypeDef(
            code="dlt", name="大乐透", region="CN",
            main_range=NumberRange(1, 35, 5),
            bonus_range=NumberRange(1, 12, 2),
        )
        assert lt.code == "dlt"

    def test_no_bonus_range(self) -> None:
        lt = LotteryTypeDef(
            code="ssq", name="双色球", region="CN",
            main_range=NumberRange(1, 33, 6),
        )
        assert lt.bonus_range is None

    def test_lottery_type_is_frozen(self) -> None:
        lt = LotteryTypeDef(code="test", name="Test", region="CN", main_range=NumberRange(1, 10, 3))
        with pytest.raises(Exception):
            lt.code = "changed"
