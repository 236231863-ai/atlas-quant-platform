# Atlas Quant Platform v4.0.0 架构报告

> Personal Decision Intelligence Layer 架构设计
> 日期：2026-08-03

---

## 1. 分层架构

```
engine/                          # v4.0.0 新增个人决策层
├── user_behavior/               # Phase 1 用户行为分析
│   ├── __init__.py              # （兼容旧 BehaviorAnalyzer）
│   └── behavior.py              # BetBehaviorAnalyzer / UserBehaviorReport
├── budget_manager/              # Phase 2 个人资金管理
│   ├── __init__.py
│   └── budget.py                # BudgetPlanner / BudgetHealthReport
├── personal_review/             # Phase 3 历史投注复盘
│   ├── __init__.py
│   └── review.py                # PersonalReviewEngine / PersonalReviewReport
├── lottery_quant/report/        # Phase 4 报告升级（个人视角）
│   └── generator.py             # QuantReportGenerator + _behavior + _improvements
└── assistant/                   # Phase 5 AI 助手升级
    ├── registry.py              # personal_analyze 工具
    └── router.py                # 优先级：PendingTask>兑奖>个人>量化>LLM
```

## 2. 复用已有模块（原则4）

| 新模块 | 复用 | 说明 |
|--------|------|------|
| user_behavior | `ticket_system.TicketManager` | 票据数据源（buy_date/cost/front/back）|
| budget_manager | `ticket_system.TicketManager` | 从票据计算实际投入 |
| personal_review | `lottery_intent.draw_matcher` | 精确开奖匹配（防穿越）|
| personal_review | `lottery_intent.prize_calculator` | 中奖金额计算 |
| report 升级 | `user_behavior` + `personal_review` | 个人行为/复盘章节 |
| personal_analyze | `TicketManager` + `BudgetPlanner` | AI 工具数据源 |

## 3. AI 助手路由优先级（v4.0.0 Phase 5）

```
用户输入
  ↓
① PendingTask 确认 → 恢复兑奖任务
  ↓
② 兑奖工具（prize：中奖/奖金/兑奖）
  ↓
③ 个人分析（personal_analyze：复盘/预算/行为，强词加权 ×2）
  ↓
④ 量化分析（quant_analyze：分析/风险/模拟）
  ↓
⑤ 普通 LLM
```

注册顺序：prize → personal_analyze → quant_analyze → hot_cold → recommend → backtest → report

## 4. 数据流

```
用户输入票据
  ↓ TicketManager（保存）
  ↓
├── BetBehaviorAnalyzer → 行为报告（投注/月年投入/追号/风险等级）
├── BudgetPlanner → 预算健康（月/年占比/超额提醒）
├── PersonalReviewEngine → 复盘报告（投入/中奖/收益比）
└── QuantReportGenerator → 5 部分个人视角报告
  ↓
个人中心（ProfilePage）+ AI personal_analyze
```

## 5. 关键设计决策

1. **兼容旧接口**：`user_behavior/__init__.py` 保留旧 BehaviorAnalyzer（unit 测试用），新增 BetBehaviorAnalyzer
2. **精确开奖匹配**：复盘复用 DrawResultMatcher 精确日期匹配，防穿越历史
3. **强词加权**：personal 强词（复盘/预算/行为）×2 优先于量化
4. **持久化隔离**：BudgetPlanner 支持 ATLAS_STORAGE_DIR 环境变量（测试隔离）
5. **免责声明贯穿**：所有 Report 含随机性声明 + 行为风险提示
6. **30 秒流程**：核心链路（解析→保存→分析→风险→报告→预算）<30s

## 6. 页面架构

```
MainWindow（9 页面）
  ├── 数据看板 / 数据分析 / 策略实验室 / 回测中心
  ├── AI 助手（personal_analyze + quant_analyze + prize）
  ├── 研究报告 / 工作台
  ├── 量化中心（QuantPage）
  └── 个人中心（ProfilePage：票据/投入/中奖/风险/报告/趋势）
```

## 7. 依赖

- 新增独立：user_behavior / budget_manager / personal_review（无循环依赖）
- 复用：ticket_system / lottery_intent / lottery_quant / evaluation_v2 / export
- 打包：atlas_desktop.spec 已加入全部新模块
