# Atlas v4.5 架构报告（Architecture Report）

版本：v4.5.0 · 2026-08-04

## 新增模块

| 模块 | 职责 | 依赖/复用 |
|------|------|----------|
| `engine/data_center/providers.py` | DataProvider 链（官方/备用/本地缓存）+ fetch_with_fallback | data_center_v2.sources/updater |
| `engine/data_center/validation.py` | DrawValidator（期号/日期/前后区/范围校验） | — |
| `engine/data_center/health.py` | DataHealthReport（各彩种状态） | providers |
| `engine/draw_monitor/monitor.py` | DrawMonitor（开奖日监控 + 事件） | live_draw.service + LotterySchedule |
| `engine/draw_monitor/notifier.py` | WindowsNotifier（Toast→msg→日志） | subprocess/PowerShell |
| `engine/user_events/report.py` | BehaviorReporter + UserBehaviorReport | user_events |

## 数据流（v4.5 完整链路）

```
官方 API ──► DataProvider 链（校验）──► 本地缓存 ~/.atlas/raw
                                          │
DrawMonitor（开奖日检测）◄────────────────┘
    │ check_once
    ▼
draw_updated 事件 ──► AutoClaimLink ──► 兑奖（含信任字段）
    │
    └──► WindowsNotifier ──► 后台提醒（关软件仍收）
    │
    └──► user_events（埋点）──► UserBehaviorReport
```

## 关键设计

- **Provider 链降级**：官方 → 备用 → 本地（彩种用正确 gameNo）
- **校验前置**：任何更新先 DrawValidator，失败不写缓存（防覆盖）
- **事件驱动**：draw_updated 触发兑奖 + 提醒 + 埋点（解耦）
- **通知降级链**：Toast → msg → 日志（后台可靠）
- **兑奖信任**：报告含来源/期号/更新时间/校验状态

## 修改文件

- `engine/claim_center/claim.py`：AutoClaimReport 信任字段 + trust_text
- `engine/user_events/events.py`：+3 事件类型
- `tools/atlas_worker.py`：同步后自动提醒
- `packaging/atlas_desktop.spec`：+8 模块

## 测试数量

- tests/v450 新增 279 场景

## 已知限制

- 双色球官方 API 不可用（235 → 0 条），降级内置
- 后台通知依赖 Windows 通知服务
