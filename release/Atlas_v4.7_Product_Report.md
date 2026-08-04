# Atlas v4.7 产品报告（Product Report）

版本：v4.7.0 · 个人彩票行为分析助手 · 2026-08-05

## 定位

**帮助用户看懂自己的购彩行为，而不是预测彩票。**

核心红线：禁止中奖预测 / 号码预测 / 提高中奖概率；明示「开奖随机，任何号码理论概率相同」。

## 修改内容

| Phase | 内容 | 文件 |
|-------|------|------|
| P1 | 用户投注历史分析引擎（10 指标画像） | engine/behavior_analysis/analysis.py |
| P2 | 投注健康评分（四维，非中奖） | engine/behavior_analysis/score.py |
| P3 | 资产报告 2.0（年度 ROI/最大回撤/中奖分布） | engine/asset_center/asset.py |
| P4 | 策略复盘系统（固定/随机/倍投/重复/冷热） | engine/strategy_review/ |
| P5 | AI 助手行为分析工具 | engine/assistant/registry.py + router.py |
| P6 | 每周彩票报告（留存） | engine/behavior_analysis/weekly.py |
| P7 | Red Team | release/Atlas_v4.7_RedTeam.md |

## 用户价值（5 场景）

1. 最近一年花多少钱 → 行为画像（总投入/净收益/ROI）
2. 中奖率怎么样 → win_rate + 等级分布
3. 投注方式是否重复 → 策略复盘（重复比例/倍投）
4. 购彩风险等级 → 健康分（四维）
5. 过去方法有没有效果 → 年度 ROI/最大回撤

## 测试

- tests/v470 新增 **841**（≥800 达标）

## 已知限制

- 行为分析需足够票据数据（冷启动）
- 双色球官方源不可用（保持内置）

## 红线

无预测、无推荐、无提高中奖概率宣传
