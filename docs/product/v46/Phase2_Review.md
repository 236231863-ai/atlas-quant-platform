# Atlas v4.6 Phase 2 Product Review：Windows 后台提醒系统

> 2026-08-04

## 产品目标

解决 v4.3 最大问题「软件关闭后无法提醒」：Task Scheduler 唤起 worker 时，按开奖日程发送开奖前 24h/3h 提醒 + 开奖后兑奖提醒。

## 交付

| 模块 | 功能 |
|------|------|
| `engine/draw_monitor/reminder_schedule.py` | ReminderScheduler：24h/3h/开奖后提醒计划 + 当天去重 |
| `tools/atlas_worker.py` | 计划任务唤起时按计划发送提醒 |

## 提醒时机

- 开奖前 24h：`📅 大乐透明日开奖`
- 开奖前 3h：`⏰ 大乐透即将开奖`
- 开奖后：`🎯 大乐透已开奖`（自动兑奖）

## 去重

`~/.atlas/reminder_sent.json` 记录每天已发类型，当天不重复打扰。

## 测试

- tests/v460/test_reminder_schedule_v460.py：26 场景
- 覆盖：24h/3h/开奖后计划、去重、文件持久化、矩阵

## 验收

- ✅ 关闭 Atlas 后（计划任务 worker）仍发提醒
- ✅ 电脑重启/软件未启动，计划任务自动恢复（schtasks 自愈）
- ✅ 提醒去重不打扰

**P2 通过，进入 P3。**
