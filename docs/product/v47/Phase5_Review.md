# Atlas v4.7 Phase 5 Product Review：AI 助手融合

> 2026-08-05

## 产品目标

AI 助手理解「分析我买彩票情况/亏很多/购彩习惯」→ 调用行为分析/健康评分。优先级：PendingTask→兑奖→行为→资产→LLM。

## 交付

| 文件 | 修改 |
|------|------|
| `engine/assistant/registry.py` | 新增 behavior_analyze 工具 + BEHAVIOR_STRONG_WORDS 加权 |
| `engine/assistant/router.py` | 路由 behavior 强词加权 |

## 支持语句

- 「分析我今年买彩票情况」→ 行为画像
- 「我是不是亏很多」→ 资产/行为
- 「我的购彩习惯怎么样」→ 健康评分

## 测试

- tests/v470/test_router_v470.py：23 场景（工具注册/路由/优先级/兑奖优先）

**P5 通过，进入 P6。**
