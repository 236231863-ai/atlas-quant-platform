# Atlas v4.4 架构报告（Architecture Report）

版本：v4.4.0 · 2026-08-04

## 新增模块

| 模块 | 职责 | 桌面入口 |
|------|------|---------|
| `engine/live_draw/events.py` | DrawEventBus 事件总线 + DrawUpdated/NewIssue/UpdateFailed/Skipped | 事件订阅（UI/兑奖） |
| `engine/live_draw/service.py` | LiveDrawService：check_once/sync_all/should_check/auto_sync_loop | 后台线程 + 计划任务 |
| `engine/live_draw/background.py` | BackgroundServiceManager（schtasks 计划任务安装/卸载/状态） | CLI/服务 |
| `engine/live_draw/health.py` | DataHealthCenter（可信等级 A-D） | 首页开奖状态卡片 |
| `engine/live_draw/claim_link.py` | AutoClaimLink（draw_updated→auto_claim→通知） | 自动触发 |
| `tools/atlas_worker.py` | 后台同步 worker（计划任务唤起） | 计划任务 |

## 数据流（v4.4 完整链路）

```
官方 API ──► IncrementalUpdater ──► ~/.atlas/raw/*.csv
                  │
                  ▼
LiveDrawService.check_once ──► DrawUpdated 事件
                  │                    │
    should_check(开奖日/过期)          ▼
                  │            AutoClaimLink → ClaimCenter → 通知
                  ▼
      DataHealthCenter（可信等级）→ 首页卡片
```

## 关键设计

- **防旧覆盖三层**：updater no_new（无新不写）/ _valid_remote（非法过滤）/ live_draw 事件驱动
- **事件解耦**：DrawEventBus 让 updater→UI/兑奖 解耦（订阅/发布）
- **后台双通道**：① 启动线程（即时）② 计划任务每 30 分钟（软件关闭仍同步）
- **静默降级**：网络/API 异常不中断，DataHealth 展示状态

## 依赖

- 无新外部依赖；schtasks（Windows 自带）
- spec 追加 live_draw 5 模块

## 架构原则

- 复用 v4.3 的 IncrementalUpdater / ClaimCenter / LotterySchedule（不重复造轮子）
- 事件驱动 UI 刷新（替代轮询）
- 全部新模块有入口（后台服务/首页卡片/自动兑奖）
