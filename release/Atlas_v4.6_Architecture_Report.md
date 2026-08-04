# Atlas v4.6 架构报告（Architecture Report）

版本：v4.6.0 · 2026-08-04

## 新增模块

| 模块 | 职责 | 复用 |
|------|------|------|
| `engine/user_analytics/analytics.py` | AnalyticsTracker（标准化事件 {event_name,timestamp,user_id,source,metadata}） | — |
| `engine/user_analytics/funnel.py` | 漏斗（打开→保存→查看→兑奖→报告） | analytics |
| `engine/user_analytics/retention.py` | Retention（D1/D3/D7 + 活跃天数） | analytics |
| `engine/draw_monitor/reminder_schedule.py` | ReminderScheduler（24h/3h/开奖后提醒计划 + 去重） | LotterySchedule |
| `engine/asset_center/monthly.py` | MonthlyReportBuilder（月度复盘） | PrizeCalculator |
| `engine/premium/feature_test.py` | PremiumFeatureTest（功能状态 + 埋点） | user_analytics |

## 数据流（v4.6）

```
用户行为 → AnalyticsTracker（~/.atlas/analytics_v46.jsonl）
              ├─ FunnelBuilder → 漏斗
              └─ RetentionBuilder → D1/D3/D7

Task Scheduler → worker → ReminderScheduler → 开奖前 24h/3h 提醒
首页 → _claim_summary（待开奖/已中奖/待领取）→ 兑奖报告
资产 → MonthlyReportBuilder → 月度复盘（诚实负期望）
免费用户 → PremiumFeatureTest → 升级解锁提示 + premium_view/click
```

## 关键设计

- **事件标准化**：8 事件统一 {event_name, timestamp, user_id, source, metadata}
- **漏斗去重**：按 user_id 去重统计各阶段人数
- **提醒计划**：开奖前 24h/3h + 当天去重（reminder_sent.json）
- **诚实资产**：月度净收益 = 中奖 - 投入（负期望不隐藏）
- **商业化验证**：只埋点不支付

## 修改文件

- `desktop/pages/first_run_dialog.py`（价值引导 + onboarding 事件）
- `desktop/pages/dashboard_page.py`（兑奖汇总卡片）
- `tools/atlas_worker.py`（提醒计划接入）
- `engine/user_analytics/analytics.py`（+premium 事件）
- `packaging/atlas_desktop.spec`（+7 模块）

## 测试数量

- tests/v460 新增 1076 场景

## 已知限制

- 双色球官方源不可用（降级内置）
- premium 无支付链路
