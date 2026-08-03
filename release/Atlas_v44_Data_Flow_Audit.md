# Atlas v4.4 数据链路审计（Data Flow Audit）

版本：v4.4 P0 · 2026-08-04 · 只读审计（禁止改代码）

## 审计范围

`APIDatasource` / `Updater` / `DataLoader` / `DrawResultMatcher` / `Notification`

## 五问审计

### 1. 当前开奖数据多久更新一次？

| 结论 | 证据 |
|------|------|
| **仅启动时更新一次，且 24h 限频** | `main_window.py:109-112` 启动时后台线程调 `maybe_update_draws`；`updater.should_update()` 24h 内跳过 |
| **无定时检查** | 全代码无 `QTimer`/`schedule`/定时循环（除 `tools/atlas_worker.py` 有 `while True + sleep` 但未接入产品） |
| **开奖后需等用户下次启动才更新** | 无开奖时刻触发机制 |

**结论：开奖数据不实时——停留在「用户启动时刻」，与真实开奖（周一/三/六大乐透、周二/四/日双色球）脱节。**

### 2. 数据源是什么？

| 源 | 实现 | 状态 |
|----|------|------|
| 官方体彩 API | `APIDatasource`（webapi.sporttery.cn，dlt gameNo=85） | ✅ 大乐透可用 |
| 双色球 API | 同接口 gameNo=235 | ❌ 当前返回 0 条（接口不再支持） |
| 内置历史 CSV | `data/raw/{lottery}_history.csv`（1200/500 期） | ✅ |
| 用户缓存 | `~/.atlas/raw/{lottery}_history.csv`（更新器写入） | ✅ 优先读取 |

### 3. 更新失败如何处理？

| 失败场景 | 处理 |
|----------|------|
| 无网络 | `urllib.urlopen` 超时 → 异常捕获 → 返回 `{error, reason: exception}` 静默降级 |
| API 返回空 | 返回 `{reason: no_remote_data}`，不写文件 |
| 无新增期号 | 返回 `{reason: no_new}`，**不写文件**（防覆盖） |
| 非法号码 | `_valid_remote` 过滤（数量/范围校验） |
| 用户 UI | **无提示**——更新失败用户无感知，数据保持旧版 |

### 4. UI 如何知道数据变化？

| 结论 | 证据 |
|------|------|
| **UI 完全不知道** | Dashboard 在 `__init__` 加载一次 `load_draws()`；无刷新回调、无数据变化事件、无轮询 |
| **无 DrawUpdated 事件** | 无事件总线 / 信号机制连接 updater → UI |
| **用户重启才看到新数据** | 更新写缓存后，需重启 Atlas 才重新加载 |

### 5. 是否存在旧数据覆盖风险？

| 风险 | 状态 | 说明 |
|------|------|------|
| 旧数据覆盖新数据 | ✅ 已防御 | v4.3.1 `no_new`（无新增不写）+ `_valid_remote`（非法过滤） |
| 双色球被写错 | ✅ 已修复 | APIDatasource gameNo 按彩种切换；API 空则降级不写 |
| **新数据被旧 UI 展示** | ⚠️ 存在 | 缓存已更新但 UI 无刷新机制，展示旧数据直到重启 |
| **开奖后无自动更新** | ⚠️ 存在 | 无定时任务，用户不启动则数据停留 |

## 审计结论

| 维度 | 现状 | v4.4 目标 |
|------|------|----------|
| 更新频率 | 启动时 + 24h 限频 | **后台定时自动同步**（开奖节奏驱动） |
| 数据源 | API + 内置 + 缓存 | 保持（大乐透实时 + 双色球降级） |
| 失败处理 | 静默降级 | 静默降级 + **Data Health 可见** |
| UI 感知 | 无事件 | **DrawUpdated 事件 → 首页卡片刷新** |
| 覆盖风险 | 已防御写坏 | 保持防御 + **可信等级监控** |

**核心缺口（v4.4 要解决）**：
1. **无后台定时同步** → P1 Live Draw Engine + P2 后台服务
2. **UI 不感知数据变化** → DrawUpdated 事件 + P5 开奖状态卡片
3. **无数据健康可见性** → P3 Data Health Center（A-D 等级）
4. **自动兑奖不随开奖触发** → P4 联动

**P0 Review：通过。进入 P1 Live Draw Engine。**
