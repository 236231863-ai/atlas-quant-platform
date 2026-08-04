# Atlas v4.8 Phase 6 Product Review：AI 助手融合

> 2026-08-05

## 产品目标

AI 支持「帮我建立彩票档案」→ import / 「分析我的彩票」→ behavior / 「我亏了多少」→ asset。

## 交付

| 文件 | 修改 |
|------|------|
| `engine/assistant/registry.py` | 新增 import_analyze 工具 + behavior 亏损→资产分支 |

## 支持语句

- 「帮我建立彩票档案」→ 引导 4 种导入方式
- 「01 05 12 23 30 + 06 08」→ 直接导入
- 「我亏了多少」→ 资产净收益
- 无票据时行为分析 → 引导建档

## 优先级

PendingTask → 兑奖 → 导入 → 行为 → 资产 → LLM

## 测试

- tests/v480/test_router_v480.py：24 场景（建档/导入/亏损/路由/工具数9）

**P6 通过，进入 P7。**
