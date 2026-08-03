# Atlas v4.4 Phase 1 Review：Live Draw Engine

> 2026-08-04

## 产品目标

从「启动更新」→「后台自动同步」：开奖数据按节奏（大乐透一/三/六、双色球二/四/日）自动检测新期、同步并**发布事件**。

## 用户场景

- 今晚大乐透开奖（周一 20:30）→ 后台服务检测到新期 26087 → 自动拉取 → 发布 draw_updated 事件 → 用户打开 Atlas 即见最新开奖（无需手动触发）。
- 用户关闭软件期间，后台仍定时检查 → 开奖结果不被错过。

## 架构设计

```
engine/live_draw/
├── events.py    DrawEventBus（订阅/发布）+ DrawUpdated/NewIssue/UpdateFailed/Skipped 事件
└── service.py   LiveDrawService（check_once / sync_all / should_check / auto_sync_loop）
     └── 复用 IncrementalUpdater（no_new 防旧覆盖 + _valid_remote 校验）
         └── 复用 LotterySchedule（开奖日程）
```

## 代码修改

| 文件 | 内容 |
|------|------|
| `engine/live_draw/events.py` | 事件总线 + DrawEvent（draw_updated/new_issue/update_failed/sync_skipped） |
| `engine/live_draw/service.py` | LiveDrawService：check_once 区分 updated/skipped/failed；should_check 开奖日+过期判断；auto_sync_loop 后台循环 |
| `engine/live_draw/__init__.py` | 导出 |

## 测试方案

- tests/v440/test_live_draw_v440.py：33 场景
- 覆盖：事件总线订阅/发布/装饰器、开奖日程（7×2 参数化）、check_once 各分支（updated/no_new/failed/api_empty）、should_check、sync_all、后台循环 stop

## 验收标准

- [x] 事件总线可订阅/发布 DrawUpdated
- [x] 开奖日判断正确（dlt 一/三/六、ssq 二/四/日）
- [x] check_once 成功/无新/失败三态正确发事件
- [x] 后台循环可优雅停止

**Review：通过。进入 P2 后台服务。**
