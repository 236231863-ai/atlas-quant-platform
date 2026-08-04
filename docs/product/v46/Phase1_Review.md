# Atlas v4.6 Phase 1 Product Review：用户事件分析系统

> 2026-08-04

## 产品目标

建立真实用户行为数据：8 类标准化事件 + 用户漏斗 + Retention Dashboard → 回答「为什么打开/回来/保存」。

## 交付

| 模块 | 功能 |
|------|------|
| `engine/user_analytics/analytics.py` | AnalyticsTracker：8 事件 {event_name, timestamp, user_id, source, metadata} |
| `engine/user_analytics/funnel.py` | 漏斗：打开→保存→查看→兑奖→报告（转化率/流失率） |
| `engine/user_analytics/retention.py` | Retention：D1/D3/D7 + 活跃天数 |

## 事件（8 类）

app_opened / ticket_saved / ticket_checked / reminder_clicked / claim_completed / report_viewed / budget_viewed / export_clicked

## 用户价值

用真实事件量化「为什么打开」——漏斗揭示哪步流失最重，Retention 揭示留存曲线。

## 测试

- tests/v460/test_analytics_v460.py：51 场景（事件格式/追踪/漏斗/留存/随机矩阵）

## 回答运营四问

- 为什么打开 → app_opened 来源分析
- 为什么保存 → ticket_saved 转化
- 为什么回来 → Retention D1/D3/D7
- 为什么付费 → premium 事件（P6）

**P1 通过，进入 P2。**
