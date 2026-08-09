# Atlas v4.9.1 — 埋点报告（Event Tracking Report）

> 模块：`engine/user_experiment/events.py` · 状态：✅ 完成
> 目标：真实用户行为全链路埋点，REAL / SIMULATION 严格隔离

---

## 一、事件集（17 项）

| 事件 | 含义 | v4.9.1 新增 |
|------|------|:---:|
| `app_install` | 安装完成 | |
| `app_open` | 打开应用 | |
| `onboarding_start` | 引导开始 | ✅ |
| `ticket_saved` | 保存彩票 | |
| `reminder_enabled` | 开启开奖提醒 | ✅ |
| `reminder_sent` | 发送开奖提醒 | ✅ |
| `draw_reminder_clicked` | 点击开奖提醒 | |
| `draw_checked` | 查看开奖结果 | ✅ |
| `draw_checked_after_reminder` | 收到提醒后查看开奖 | ✅ |
| `claim_checked` | 查看兑奖结果 | |
| `claim_completed` | 兑奖完成 | ✅ |
| `asset_viewed` | 查看资产 | ✅ |
| `report_viewed` | 查看报告 | |
| `weekly_report_viewed` | 查看周报 | ✅ |
| `premium_view` | 查看 Premium 页 | |
| `premium_click` | 点击付费意愿 | |
| `weekly_return` | 周回访（本周活跃） | |

---

## 二、里程碑（10 项）

`first_open` · `first_onboarding` · `first_ticket_saved` · `first_reminder_enabled` · `first_draw_checked` · `first_prize_checked` · `first_claim_completed` · `first_asset_viewed` · `first_report_viewed` · `first_weekly_report_viewed`

---

## 三、数据来源隔离

| 标记 | 含义 |
|------|------|
| `SOURCE_REAL` | 真实用户（含旧版 `desktop` 埋点归一） |
| `SOURCE_SIMULATION` | 模拟数据（P1 模拟器） |

- `real_events()` / `simulation_events()` 强制分离
- **统计默认只含 REAL**，禁止混合
- `import_real_events()` 支持从旧埋点（analytics_v46 / events_v43）导入并标记 REAL

---

## 四、漏斗对应

```
app_install → app_open → ticket_saved
→ reminder_enabled → draw_checked
→ claim_checked / claim_completed → weekly_report_viewed
```

---

## 五、验证

- ✅ 事件集完整性断言通过（v4.9.1 新增 8 项全部在列）
- ✅ 里程碑覆盖新增事件
- ✅ 新快捷方法（onboarding/enable_reminder/reminder_sent 等）均测试通过
- ✅ 旧埋点导入别名映射（onboarding_complete→onboarding_start 等）通过
