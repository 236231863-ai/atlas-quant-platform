"""号码解析测试：普通格式 / 连续格式 / 越界 / 重复 / 双色球。"""
from __future__ import annotations

import pytest

from backend.mobile.service import MobileTicketParser as P


class TestDltParse:
    def test_standard_format(self):
        assert P.parse("06 16 21 30 34 + 06 12", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_standard_with_leading_zero(self):
        assert P.parse("01 05 12 23 31 + 03 09", "dlt") == ([1, 5, 12, 23, 31], [3, 9])

    def test_comma_separated(self):
        assert P.parse("06,16,21,30,34|06,12", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_continuous_format(self):
        assert P.parse("06162130340612", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_continuous_15_digits(self):
        assert P.parse("01051223310309", "dlt") == ([1, 5, 12, 23, 31], [3, 9])

    def test_front_out_of_range(self):
        assert P.parse("36 01 02 03 04 + 01 02", "dlt") is None

    def test_back_out_of_range(self):
        assert P.parse("01 02 03 04 05 + 13 14", "dlt") is None

    def test_duplicate_front(self):
        assert P.parse("01 01 02 03 04 + 01 02", "dlt") is None

    def test_duplicate_back(self):
        assert P.parse("01 02 03 04 05 + 01 01", "dlt") is None

    def test_too_few_numbers(self):
        assert P.parse("01 02 03 04 + 01 02", "dlt") is None

    def test_too_many_numbers(self):
        assert P.parse("01 02 03 04 05 06 + 01 02", "dlt") is None

    def test_empty(self):
        assert P.parse("", "dlt") is None

    def test_non_numeric(self):
        assert P.parse("a b c d e + f g", "dlt") is None


class TestSsqParse:
    def test_ssq_format(self):
        front, back = P.parse("03 08 15 22 33 06 09", "ssq")
        assert len(front) == 6 and len(back) == 1

    def test_ssq_6_plus_1(self):
        front, back = P.parse("03 08 15 22 26 33 + 09", "ssq")
        assert len(front) == 6 and len(back) == 1
        assert front == [3, 8, 15, 22, 26, 33] and back == [9]

    def test_ssq_red_out_of_range(self):
        assert P.parse("34 35 36 01 02 03 + 05", "ssq") is None

    def test_ssq_blue_out_of_range(self):
        assert P.parse("01 02 03 04 05 06 + 17", "ssq") is None

    def test_ssq_wrong_count(self):
        assert P.parse("01 02 03 04 05 06 07 08 + 09", "ssq") is None


class TestParserEdge:
    def test_sorted_output(self):
        result = P.parse("34 21 06 16 30 + 12 06", "dlt")
        assert result == ([6, 16, 21, 30, 34], [6, 12])

    def test_unknown_lottery(self):
        assert P.parse("01 02 03 04 05 + 01 02", "unknown") is None

    def test_full_width_plus(self):
        assert P.parse("06 16 21 30 34 ＋ 06 12", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_trailing_spaces(self):
        assert P.parse("  06 16 21 30 34 + 06 12  ", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_newline_inside(self):
        assert P.parse("06 16 21\n30 34 + 06 12", "dlt") == ([6, 16, 21, 30, 34], [6, 12])

    def test_dlt_back_min(self):
        assert P.parse("01 02 03 04 05 + 01 01", "dlt") is None  # 重复

    def test_dlt_front_single_digit(self):
        assert P.parse("1 5 12 23 31 + 3 9", "dlt") == ([1, 5, 12, 23, 31], [3, 9])

    def test_reject_mixed_separator_ambig(self):
        # 12 个数字但包含分隔 → 按分隔解析，数量不足
        assert P.parse("06 16 21 30 34+06", "dlt") is None
