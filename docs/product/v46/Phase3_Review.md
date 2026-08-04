# Atlas v4.6 Phase 3 Product Review：首次用户引导优化

> 2026-08-04

## 产品目标

第一次打开 30 秒完成价值理解：欢迎「以后不用记彩票开奖时间」→ 保存 → 设置提醒 → 「已保护」。

## 交付

| 文件 | 修改 |
|------|------|
| `desktop/pages/first_run_dialog.py` | 步骤标题价值导向（欢迎→彩种→模式）+ 完成按钮「我的彩票已保护」+ onboarding 事件 |

## 事件统计

- onboarding_start：`app_opened` metadata onboarding=start
- onboarding_complete：`claim_completed` metadata onboarding=complete
- onboarding_drop：reject 未完成 → metadata onboarding=drop

## 用户价值

首次用户 30 秒理解「Atlas 帮我不忘彩票/自动兑奖」——从"选用途"变为"理解价值"。

## 测试

- tests/v460/test_onboarding_v460.py：20 场景（标题/步骤/事件/流程）

**P3 通过，进入 P4。**
