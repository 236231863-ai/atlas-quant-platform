# Atlas v4.4 Phase 2 Review：Atlas Background Service

> 2026-08-04

## 产品目标

软件关闭后仍自动同步开奖数据：Windows 计划任务后台唤起 worker，定时检查 + 开机启动。

## 用户场景

- 用户晚上关闭 Atlas → 次日清晨，后台计划任务已自动拉取昨晚开奖结果 → 用户打开 Atlas 即见最新。
- 无需用户手动操作，开奖数据"自动到位"。

## 架构设计

```
engine/live_draw/background.py
  BackgroundServiceManager（schtasks 计划任务管理）
    ├─ install()     创建 AtlasLiveDrawSync（每30分钟）+ Boot（开机启动）
    ├─ uninstall()   删除任务
    └─ status()      查询安装/运行状态

tools/atlas_worker.py（被计划任务唤起）
    ├─ sync_once()   智能同步所有彩种后退出（计划任务模式）
    └─ run_loop()    后台长驻循环（--loop 模式）
```

## 代码修改

| 文件 | 内容 |
|------|------|
| `engine/live_draw/background.py` | BackgroundServiceManager（schtasks Create/Delete/Query，隐藏窗口） |
| `tools/atlas_worker.py` | 升级为真正的同步 worker（sync_once/run_loop + sys.path 修复） |

## 测试方案

- tests/v440/test_background_v440.py：15 场景
- 覆盖：install/uninstall/status 的 schtasks 命令 mock、开机触发器、worker 缺失处理、CLI、常量
- worker 真实运行验证：`python tools/atlas_worker.py --once` → dlt/ssq 均 sync_skipped（数据已最新）

## 验收标准

- [x] 安装计划任务（MINUTE 30 + ONSTART 开机）
- [x] 卸载、状态查询
- [x] worker 同步一次正常退出
- [x] 软件关闭仍可运行（独立计划任务）

**Review：通过。进入 P3 数据可信中心。**
