# Atlas v4.9 P1 用户行为埋点报告

> 阶段：P1 · 类型：真实用户验证基础设施
> 目的：让「用户为什么打开 / 保存 / 回来」第一次有数据可答，而非猜测

## 一、事件集（已实现，全部可 CSV 导出）

| 事件 | 含义 | 所属验证问题 |
|------|------|-------------|
| `app_install` | 安装完成 | Q1 安装完成率 |
| `app_open` | 打开应用 | 留存（D1/D3/D7） |
| `ticket_saved` | 保存彩票 | Q2 首次建档率 / WALU |
| `draw_reminder_clicked` | 点击开奖提醒 | 提醒点击率 / WALU |
| `claim_checked` | 查看兑奖结果 | WALU / 兑奖查看率 |
| `report_viewed` | 查看报告 | 报告查看率 |
| `premium_view` | 查看 Premium 页 | Q4 付费意愿 |
| `premium_click` | 点击付费意愿 | Q4 付费意愿 |
| `weekly_return` | 周回访 | 周留存 |

每个事件记录：`experiment_id / user_id / event_name / timestamp / source / metadata`

## 二、里程碑（首次发生时间）

| 里程碑 | 对应事件 | 价值 |
|--------|---------|------|
| `first_open_at` | app_open | 安装→激活耗时 |
| `first_ticket_saved_at` | ticket_saved | **首次建档时刻**（Q2 关键） |
| `first_prize_checked_at` | claim_checked | 首次体验「自动兑奖」价值 |
| `first_report_viewed_at` | report_viewed | 首次体验「复盘」价值 |

## 三、数据存储

- 事件文件：`~/.atlas/experiments_v49.jsonl`（支持 `ATLAS_STORAGE_DIR` 隔离）
- CSV 导出：`experiments_v49_export.csv`（utf-8-sig，Excel 友好）
- 引擎：`engine/user_experiment/events.py`

## 四、实现方式

```text
埋点(desktop/engine) → ExperimentTracker.record()
  → jsonl 追加写（本地，脱敏风险低）
  → export_csv() 导出
  → milestones() 首次事件时间
```

## 五、已知限制

- 当前为本地单机埋点，无云端汇聚（P4 仪表盘前仅本地 CSV 分析）
- 事件名集合为白名单，未登记事件会被拒绝（防脏数据）
