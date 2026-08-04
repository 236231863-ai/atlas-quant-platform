# Atlas v4.8 Phase 3 Product Review：新用户引导系统

> 2026-08-05

## 产品目标

首次打开不展示研究数据，展示价值三步：建档案 → 看购彩 → 开提醒。

## 交付

| 模块 | 功能 |
|------|------|
| `engine/onboarding/flow_v48.py` | OnboardingFlow：三步流程 + start/complete/drop 事件 |

## 三步

1. 建立我的彩票档案
2. 看看我的购彩情况
3. 开启开奖提醒

## 测试

- tests/v480/test_onboarding_v480.py：33 场景（三步/事件/价值导向/无研究数据）

**P3 通过，进入 P4。**
