# Atlas v4.4 Phase 5 Review：首页开奖状态卡片

> 2026-08-04

## 产品目标

用户打开首页 3 秒看到**开奖实时状态**：距离下一开奖 / 最新开奖 / 数据可信 / 待兑奖票据。

## 用户场景

- 用户打开 Atlas → 首页「📡 开奖状态」卡片：`距离下一开奖：大乐透 2026-08-05 · 双色球 2026-08-04` + `数据可信 A 级 · 最新 26087（2026-08-03）· 3 小时前` + `待兑奖 N 张`。
- 数据可信度一目了然（A-D 级），旧数据可感知。

## 架构设计

```
dashboard_page._draw_status_card()
  ├─ LotterySchedule.next_draw_date → 距离下一开奖（大乐透+双色球）
  ├─ DataHealthCenter.check('dlt') → 最新期/日期/年龄/等级
  └─ ClaimCenter.pending_list → 待兑奖数量
```

## 代码修改

| 文件 | 内容 |
|------|------|
| `desktop/pages/dashboard_page.py` | `_draw_status_card()` 方法 + `_build` 插入卡片 |

## 测试方案

- tests/v440/test_dashboard_v440.py：24 场景
- 覆盖：卡片标题/距离/健康/待兑奖、无票据、有票据、重复实例、数量矩阵

## 验收标准

- [x] 卡片含「距离下一开奖 / 最新开奖 / 数据可信 / 待兑奖」
- [x] 无票据显示「待兑奖 0 张」
- [x] 数据可信等级可见

**Review：通过。进入 P6 测试（≥800）。**
