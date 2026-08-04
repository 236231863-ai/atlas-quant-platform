# Atlas v4.7 架构报告（Architecture Report）

版本：v4.7.0 · 2026-08-05

## 新增模块

| 模块 | 职责 | 复用 |
|------|------|------|
| `engine/behavior_analysis/analysis.py` | BehaviorAnalyzer（10 指标画像） | PrizeCalculator |
| `engine/behavior_analysis/score.py` | BehaviorScore（四维健康分） | analysis |
| `engine/behavior_analysis/weekly.py` | WeeklyReport（每周报告） | analysis |
| `engine/strategy_review/review.py` | StrategyReviewer（策略复盘） | — |
| `engine/asset_center/asset.py` | AnnualSummary +ROI/回撤/分布 | — |

## 数据流

```
TicketManager 票据 → BehaviorAnalyzer → 投注画像（10指标）
                 → BehaviorScore → 健康分（非中奖）
                 → StrategyReviewer → 策略复盘
                 → WeeklyReport → 每周报告
                 → AssetCenter → 年度报告（ROI/回撤/分布）
                 → AI Router（behavior_analyze）→ 问答
```

## 关键设计

- **真实数据驱动**：全部指标来自历史票据 + 真实开奖匹配
- **非预测**：只分析过去，不输出「下一期」建议
- **健康分四维**：资金管理40/投注纪律30/复盘习惯20/风险意识10
- **AI 加权**：BEHAVIOR_STRONG_WORDS 让行为分析优先于 personal/quant

## 修改文件

- `engine/assistant/registry.py`（behavior_analyze + 强词）
- `engine/assistant/router.py`（行为加权）
- `engine/asset_center/asset.py`（年度报告增强）
- `packaging/atlas_desktop.spec`（+6 模块）

## 测试数量

- tests/v470 新增 841 场景

## 已知限制

- 双色球源不可用
- 冷启动需数据积累
