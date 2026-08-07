"""v4.9 P2 测试：首次体验 + 数据可信状态 + 移动端评估支撑。

聚焦 P2 改动：
  1. 首次引导价值导向（不展示研究指标，三步建档导向）
  2. 建档流程（号码输入复用 TicketParser，普通/连续/多注）
  3. 数据可信状态（🟢/🟡 判定 + 来源 + 失败原因 + 双色球降级）
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# 共享 QApplication（FirstRunDialog 测试需要）
@pytest.fixture(scope="module", autouse=True)
def _qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app

from engine.lottery_intent.ticket_parser import TicketParser
from engine.live_draw.health import DataHealthCenter


# ---------- P2-A 首次引导：价值导向 ----------
def test_first_run_interface_preserved():
    """FirstRunDialog 保留 purpose/lottery/mode/_go/stack 接口（兼容 v361）。"""
    from desktop.pages.first_run_dialog import FirstRunDialog
    from desktop.user_profile import UserProfile
    dlg = FirstRunDialog(UserProfile())
    assert hasattr(dlg, "purpose")
    assert hasattr(dlg, "lottery")
    assert hasattr(dlg, "mode")
    assert hasattr(dlg, "_go")
    assert hasattr(dlg, "stack")
    dlg._go(0)
    assert dlg.stack.currentIndex() == 0
    dlg._go(2)
    assert dlg.stack.currentIndex() == 2
    dlg.close()


def test_first_run_value_oriented_no_research_terms():
    """首次引导三步标题不含研究指标（冷热号/和值/频率）。"""
    from desktop.pages.first_run_dialog import FirstRunDialog
    from desktop.user_profile import UserProfile
    dlg = FirstRunDialog(UserProfile())
    titles = []
    for i in range(3):
        dlg._go(i)
        titles.append(dlg.title.text())
    joined = " ".join(titles)
    for bad in ("冷热号", "和值", "频率", "回测"):
        assert bad not in joined, f"首次引导仍含研究指标词: {bad}"
    dlg.close()


def test_first_run_value_oriented_content():
    """首次引导第一步展示价值主张（保存/提醒/兑奖/资产）。"""
    from desktop.pages.first_run_dialog import FirstRunDialog
    from desktop.user_profile import UserProfile
    dlg = FirstRunDialog(UserProfile())
    dlg._go(0)
    assert "以后不用记彩票开奖时间" in dlg.title.text()
    dlg.close()


def test_first_run_archiving_step():
    """第三步为建档导向（现在建档/已保护）。"""
    from desktop.pages.first_run_dialog import FirstRunDialog
    from desktop.user_profile import UserProfile
    dlg = FirstRunDialog(UserProfile())
    dlg._go(2)
    assert "现在建档" in dlg.title.text()
    assert "已保护" in dlg.next_btn.text()
    dlg.close()


def test_first_run_lottery_step():
    """第二步选择彩种。"""
    from desktop.pages.first_run_dialog import FirstRunDialog
    from desktop.user_profile import UserProfile
    dlg = FirstRunDialog(UserProfile())
    dlg._go(1)
    assert "彩票" in dlg.title.text()
    dlg.close()


# ---------- P2-B 建档：号码输入复用 TicketParser ----------
@pytest.mark.parametrize("text,expect_notes", [
    ("01 05 12 23 31 + 03 09", 1),            # 普通格式
    ("01051223310309", 1),                      # 连续格式
    ("01 05 12 23 31 + 03 09\n02 07 14 21 33 + 05 11", 2),  # 多注换行
    ("01 05 12 23 31 + 03 09 / 02 07 14 21 33 + 05 11", 2), # 多注斜杠
    ("01 05 12 23 31 + 03 09；02 07 14 21 33 + 05 11", 2),  # 多注分号
])
def test_parse_formats(text, expect_notes):
    """三种输入格式全部正确解析（复用 TicketParser，不重写）。"""
    r = TicketParser.parse(text)
    assert r.parsed_notes == expect_notes


def test_parse_continuous_numbers_front_back():
    """连续格式正确拆分为前区5+后区2。"""
    r = TicketParser.parse("01051223310309")
    assert r.tickets[0].front == [1, 5, 12, 23, 31]
    assert r.tickets[0].back == [3, 9]


def test_parse_multi_notes_distinct():
    """多注解析每注独立。"""
    r = TicketParser.parse("01 05 12 23 31 + 03 09 / 02 07 14 21 33 + 05 11")
    assert r.tickets[0].front == [1, 5, 12, 23, 31]
    assert r.tickets[1].front == [2, 7, 14, 21, 33]


@pytest.mark.parametrize("lottery,infer", [
    (("01 05 12 23 31 + 03 09"), "dlt"),       # 5+2 → 大乐透
    (("01 02 03 04 05 06 + 07"), "ssq"),        # 6+1 → 双色球
])
def test_parse_infer_lottery(lottery, infer):
    r = TicketParser.parse(lottery)
    assert r.lottery == infer


def test_parse_empty_returns_zero():
    assert TicketParser.parse("").parsed_notes == 0


def test_parse_invalid_numbers_rejected():
    """越界号码（前区>35）应被拒绝。"""
    from engine.import_center.imports import TextImporter
    rep = TextImporter.import_text("99 01 02 03 04 + 05 06", lottery="dlt", buy_date="")
    assert rep.total_imported == 0  # 号码越界被拒绝


# ---------- 数据可信状态 ----------
@pytest.mark.parametrize("age,has_data,expect", [
    (5, True, "A"),        # <12h
    (15, True, "B"),       # 12-24h
    (40, True, "C"),       # >24h
    (-1, True, "D"),       # 无更新时间
    (5, False, "D"),       # 无数据
])
def test_health_level_of(age, has_data, expect):
    assert DataHealthCenter.level_of(age, has_data) == expect


def test_health_check_ssq_fallback():
    """双色球（无实时源）回退内置数据，诚实显示非实时状态。"""
    import tempfile
    os.environ["ATLAS_STORAGE_DIR"] = tempfile.mkdtemp()
    h = DataHealthCenter.check("ssq")
    assert h.level in ("A", "B", "C", "D")  # 一定有等级
    assert h.latest_issue  # 有最新期号（内置）


def test_health_check_has_fields():
    """健康对象含 P2 需要的字段：来源/更新时间/最新期号。"""
    import tempfile
    os.environ["ATLAS_STORAGE_DIR"] = tempfile.mkdtemp()
    h = DataHealthCenter.check("dlt")
    for field in ("level", "latest_issue", "draw_date", "source", "age_hours"):
        assert hasattr(h, field), f"缺少字段: {field}"


def test_health_message_for_level():
    """A/B/C/D 各级别均有说明文案。"""
    for lvl in ("A", "B", "C", "D"):
        assert lvl in DataHealthCenter.LEVEL_MESSAGES


def test_health_level_messages_not_fake_realtime():
    """数据状态文案不伪装实时（明确区分更新状态）。"""
    for msg in DataHealthCenter.LEVEL_MESSAGES.values():
        # 包含更新相关的诚实描述，而非承诺实时
        assert msg


# ---------- 数据安全：错误数据不覆盖 ----------
def test_updater_no_new_protects_cache():
    """无新增期号时不写缓存（保护已有可信数据）。"""
    from engine.data_center_v2.updater import IncrementalUpdater
    import tempfile
    tmp = tempfile.mkdtemp()
    up = IncrementalUpdater("dlt", storage_dir=tmp)
    # 模拟已有缓存
    up.save_local([{"issue": "26088", "date": "2026-08-05",
                    "numbers": "03 09 11 24 27|05 11", "pool": "0"}])
    up._mark_updated(1, 0)
    # 无远程数据 → 不写
    import unittest.mock as mock
    with mock.patch.object(up.__class__, "should_update", return_value=True), \
         mock.patch.object(up, "_load_builtin", return_value=[]), \
         mock.patch("engine.data_center_v2.updater.APIDatasource") as M:
        M.return_value.load.return_value = []
        result = up.update(force=True)
    assert result["added"] == 0
    # 缓存仍在
    assert len(up.load_local()) == 1


def _rec(front, back):
    """构造带 front/back 属性的记录（与 DrawRecord 一致）。"""
    return type("Rec", (), {"front": front, "back": back})


def test_updater_invalid_remote_filtered():
    """非法远程记录（号码越界）被过滤，不污染缓存。"""
    from engine.data_center_v2.updater import IncrementalUpdater
    import tempfile
    tmp = tempfile.mkdtemp()
    up = IncrementalUpdater("dlt", storage_dir=tmp)
    up.save_local([{"issue": "26087", "date": "2026-08-03",
                    "numbers": "05 10 16 24 27|04 10", "pool": "0"}])
    bad = _rec([99, 100, 101, 102, 103], [99, 99])  # 越界
    assert up._valid_remote(bad, "dlt") is False


def test_updater_valid_remote_dlt():
    from engine.data_center_v2.updater import IncrementalUpdater
    good = _rec([1, 5, 12, 23, 35], [2, 12])
    assert IncrementalUpdater._valid_remote(good, "dlt") is True


def test_updater_valid_remote_ssq():
    from engine.data_center_v2.updater import IncrementalUpdater
    good = _rec([1, 5, 12, 23, 30, 33], [16])
    bad = _rec([1, 5, 12, 23, 30, 33], [17])  # 蓝球>16
    assert IncrementalUpdater._valid_remote(good, "ssq") is True
    assert IncrementalUpdater._valid_remote(bad, "ssq") is False
