# Atlas v4.5 Phase 3 Product Review：Windows 后台提醒

> 2026-08-04

## 产品目标

解决「必须打开软件才能提醒」：后台 worker 检测到新开奖/中奖/待兑奖 → Windows 通知（无需软件运行）。

## 交付

| 模块 | 功能 |
|------|------|
| `engine/draw_monitor/notifier.py` | WindowsNotifier：Toast(原生) → msg(会话) → 日志(兜底) 三级降级链 |
| `tools/atlas_worker.py` | 同步后对 draw_updated 事件自动发提醒 |

## 通知通道

1. **PowerShell Windows Toast**（原生通知，无需软件运行）
2. **msg.exe**（登录会话消息框，降级）
3. **通知日志**（~/.atlas/notifications.jsonl，兜底可查）

## 测试

- tests/v450/test_notifier_v450.py：15 场景
- 覆盖：日志兜底、统一入口降级链、开奖/中奖/待兑奖提醒、命令构造、事件→通知

## 验收

- [x] 后台 worker 可发通知（关闭主窗口后由计划任务 worker 触发）
- [x] 通知通道有降级（Toast 不可用 → msg → 日志）

## 用户价值

用户关闭软件仍能收到开奖/中奖/待兑奖提醒——「Atlas 主动找我」而非「我找 Atlas」。

**P3 通过，进入 P4。**
