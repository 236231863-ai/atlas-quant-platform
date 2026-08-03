# Atlas v4.1.1 架构报告

> Retention Optimization Sprint · 2026-08-03

---

## 新增/强化模块

### engine/reminder_center（强化）
- `ticket_status()`：票据状态机（待开奖/已开奖待兑奖/已兑奖）
- `notify_text()`：桌面通知文案生成

### desktop/pages/reminder_notifier.py（新增）
- QSystemTrayIcon 桌面通知（无第三方依赖）
- 点击通知回调（跳兑奖页）

### engine/budget_manager（强化）
- `consecutive_weeks()`：连续购买周数
- `reminders()`：预算提醒（达80%/连续购买）

### desktop/pages/dashboard_page.py（重构）
- 6 项价值指标（票/开奖/待兑/本月投入/本月结果/状态）
- 动态话术（待兑奖/上月对比/30天中奖）
- 首次引导卡片

## 数据流

```
票据 → 状态机 → 提醒引擎 → 桌面通知 → 点击 → 兑奖
     → 预算 → 提醒（80%/连续）→ 首页价值面板
```

## 复用
- LotterySchedule（开奖日程）
- PersonalReviewEngine（本月结果）
- BudgetPlanner（预算）
- 全部复用，零新增孤立模块
