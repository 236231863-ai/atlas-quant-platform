# Atlas v4.9 P2 实时开奖数据链路审计报告

> 性质：架构审计 + 最小可靠性改造（本阶段未大规模重写数据系统）
> 方法：实际检查代码链路 DataSource→Updater→Cache→DataLoader→PrizeCalculator→UI，非设计文档

## 一、数据链路全景

```
DataSource（APIDatasource 官方体彩 API）
   ↓
Updater（IncrementalUpdater：合并去重/校验/限频）
   ↓
Cache（~/.atlas/raw/{lottery}_history.csv 用户缓存）
   ↓
DataLoader（desktop/data_loader.py 用户缓存优先）
   ↓
PrizeCalculator（engine/lottery_intent 兑奖计算）
   ↓
UI（首页开奖状态卡 + 兑奖报告）
```

## 二、8 问实证回答

### Q1. 大乐透数据来源是什么？
**官方体彩 API**（`webapi.sporttery.cn`, gameNo=85）。实测：返回 30 条，最新 **26088 期（2026-08-05）** `03 09 11 24 27|05 11`，奖池 7.92 亿。
`APIDatasource`（`engine/data_center_v2/sources.py`）→ 30 条/页，可翻页。

### Q2. 双色球数据来源是什么？
**官方 API 声明支持（gameNo=235），但当前实测返回 0 条**——该接口不再支持双色球。因此双色球**实时更新暂不可用**，保持内置 **500 期有效数据**（最新 2026087），且**不写入错误数据**（updater 过滤空源）。

### Q3. 数据多久更新一次？
- 桌面启动时后台线程静默拉取
- `IncrementalUpdater` 限频 **24h 内只更新一次**（meta 文件记录 `data_last_update_{lottery}.json`）
- 后台计划任务每 30 分钟唤醒 worker（若已安装）

### Q4. Atlas 启动时是否自动更新？
**是**。`main_window.py` 启动时 `threading.Thread(target=maybe_update_draws)`，不阻塞 UI，无网静默降级。真实环境 meta 显示 `updated=2026-08-05T22:52:15`，说明启动更新在运行。

### Q5. 软件关闭时是否还能更新？
**是（可选安装）**。`BackgroundServiceManager`（`engine/live_draw/background.py`）通过 Windows 计划任务 `AtlasLiveDrawSync`，每 30 分钟运行 `atlas_worker.py`，支持开机启动触发器。前提：需用户安装（`install()`）。

### Q6. 错误数据是否可能覆盖正确缓存？
**不会**。三层保护：
1. **`_valid_remote`**：号码数量/范围校验（大乐透 5+2 / 1-35 / 1-12；双色球 6+1 / 1-33 / 1-16），非法记录过滤
2. **`no_new`**：无新增期号**不写文件**，绝不覆盖已有正确数据
3. **`_merge` 按期号去重**：远程仅追加/更新同期的池，不产生脏插入

### Q7. 如何判断"新开奖已经出现"？
`update()` 中：`local_issues`（本地期号集合）vs `remote`（远程期号）→ `added = [r for r in merged if r.issue not in local_issues]`。**仅当 added 非空才写缓存**（`reason: "no_new"` 时不写）。

### Q8. 数据源失效时是否继续使用最后可信数据？
**是**。三处静默降级：
- API 异常 → `except` 捕获，返回 `error`，**不写缓存**，保留本地
- API 空源 → `reason: "api_empty"`，保留本地
- UI 显示 🟡/🔴 状态（不伪装实时）+ 最后可信数据时间

## 三、数据可信机制（大乐透/双色球分别验证）

| 校验项 | 大乐透 | 双色球 | 实测 |
|--------|--------|--------|------|
| 前/红球数量 | 5 | 6 | ✅ `_valid_remote` |
| 后/蓝球数量 | 2 | 1 | ✅ |
| 前/红球范围 | 1-35 | 1-33 | ✅ |
| 后/蓝球范围 | 1-12 | 1-16 | ✅ |
| 期号合法 | ✅ | ✅ | 合并时 `int(issue)` |
| 新期号不倒退 | ✅ | ✅ | `no_new` 保护 |
| 验证失败覆盖 | ❌ 禁止 | ❌ 禁止 | 不写文件 |

**测试证据**：`tests/v490/test_p2_experience.py` 29 项（含 `test_updater_no_new_protects_cache` / `test_updater_invalid_remote_filtered` / `test_health_*`）。

## 四、实时状态 UI 可见（P2 强化）

首页「📡 开奖状态」卡片（`dashboard_page.py`）已强化：

```
🟢 A 级 正常同步 · 最新期 26088（2026-08-05）· 更新时间 2026-08-05T22:52 · 来源 实时更新（官方 API）
🟡 B/C 级 ...（12h/24h 未更新）
🔴 D 级 数据异常（暂未更新）· 最后可信数据：YYYY-MM-DD · 原因：...
```

- **禁止伪装实时**：仅 A 级显示绿色；B/C 黄、D 红
- 来源、更新时间、期号、失败原因均可见

## 五、结论

**大乐透实时更新可靠**（官方 API 工作正常 + 校验 + 保护 + UI 状态）。**双色球实时更新不可用**（官方接口返回 0），当前诚实降级为内置数据并标注状态。**数据源失败安全**（三层保护 + 保留最后可信数据）。

**遗留缺口**：
1. 双色球实时数据源（需福彩官方接口或第三方，后续 Sprint 项）
2. 后台计划任务需用户主动安装才生效
3. 无云端数据回源（纯本地缓存）
