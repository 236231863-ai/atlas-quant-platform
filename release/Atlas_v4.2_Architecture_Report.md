# Atlas v4.2 架构报告

> User Growth & Data Flywheel Sprint · 2026-08-03

---

## 1. 新增模块

| 模块 | 职责 | 入口 |
|------|------|------|
| `engine/user_archive/` | 个人彩票档案（累计购买/中奖/次数/最高奖金/周期/常购彩种） | 个人中心档案卡片 |
| `engine/auto_review/` | 自动复盘（开奖→匹配票据→生成结果报告） | 启动桌面通知 |
| `engine/growth_health/` | 购彩健康指数（预算/记录/复盘/风险四维 → A/B/C） | 个人中心成长区 |
| `engine/annual_report/` | PDF 年度报告（复用 export/PDFExporter） | 个人中心导出按钮 |
| `engine/premium/` | Atlas Premium 会员（免费/会员功能矩阵 + 门控） | 个人中心会员卡片 |
| `engine/user_simulation/` | 50 用户留存模拟（行为概率模型） | 测试/报告 |

## 2. 依赖关系

```
ticket_system (数据源)
   ├── user_archive ──→ draw_matcher + prize_calculator（中奖统计）
   ├── auto_review ──→ lottery_intent + schedule（归属期判定）
   ├── growth_health ──→ budget_manager + reminder_center（维度评分）
   ├── annual_report ──→ export/PDFExporter（PDF 输出）
   ├── premium ──→ (独立，功能门控层)
   └── user_simulation ──→ (独立，行为模型)
```

## 3. 关键设计

- **票据归属期判定**（auto_review）：显式 draw_date 精确匹配 + 购买日经 LotterySchedule 推算（开奖日当天买入=当期，周四买=周六期），杜绝串期。
- **中奖统计单一来源**：所有新模块复用 DrawResultMatcher + PrizeCalculator，与 v4.0 兑奖引擎口径一致（集成测试验证各模块结果一致）。
- **功能门控**（premium）：`PremiumManager.is_allowed(feature)` 单点判定，免费/会员权限矩阵集中定义。
- **健康指数非中奖能力**：四维加权（0.30/0.20/0.25/0.25），与中奖无关（测试断言：同样行为中不中奖等级一致）。

## 4. 未改动的核心链路

LotteryIntentRouter → TicketParser → DrawResultMatcher → PrizeCalculator 保持稳定，无回归风险。

## 5. 架构原则

- 引擎层无 UI 依赖（Qt 仅在 desktop/）。
- 新模块全部可独立测试（纯数据进出）。
- 禁止跨模块隐式依赖（各自从 TicketManager 读原始数据）。
