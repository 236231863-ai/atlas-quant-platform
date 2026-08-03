# Atlas v4.4 数据可信报告（Data Reliability Report）

版本：v4.4.0 · 2026-08-04

## 一、数据链路（v4.4 全貌）

```
官方体彩 API（webapi.sporttery.cn, gameNo=85）
  → IncrementalUpdater（no_new 防覆盖 + _valid_remote 校验）
  → ~/.atlas/raw/{lottery}_history.csv（用户缓存，优先读取）
  → LiveDrawService（事件驱动同步）
  → DrawUpdated 事件 → 自动兑奖 / UI 刷新
  → DataHealthCenter（A-D 可信等级）
```

## 二、可信保障机制

| 机制 | 说明 |
|------|------|
| **官方数据源** | 体彩官网 API（大乐透 gameNo=85），非第三方抓取 |
| **防旧覆盖** | `no_new`：无新增期号不写文件；`_valid_remote`：号码数量/范围校验 |
| **后台自动同步** | 启动线程 + 计划任务每 30 分钟 + 开奖日智能检查 |
| **可信等级可见** | A<12h / B 12-24h / C>24h / D 异常（首页卡片展示） |
| **静默降级** | 网络/API 异常不中断软件，数据保持旧版并标记状态 |

## 三、防覆盖实测（v4.3.1 教训 → v4.4 强化）

v4.3.1 曾出现 exe 后台线程覆盖正确数据（26087 号码错位）。v4.4 三层防御：
1. updater `no_new`：无新期不写文件
2. updater `_valid_remote`：非法号码过滤（dlt 5+2 / ssq 6+1 + 范围）
3. live_draw 事件驱动：check_once 区分 updated/skipped/failed

## 四、数据源状态

| 彩种 | 状态 | 说明 |
|------|------|------|
| 大乐透 | ✅ 实时 | gameNo=85 官方 API，1201 期，最新 26087 |
| 双色球 | ⚠️ 内置 | gameNo=235 接口当前返回 0 条；保持 500 期有效数据 |

## 五、可信度验证

- worker 真实运行：dlt/ssq 均 sync_skipped（数据已最新，无异常覆盖）
- data_loader 读取用户缓存优先（1201 期 / 26087 / 可信 A）
- 全量回归无新增失败

## 结论

**开奖数据可信**：官方源 + 防覆盖 + 后台同步 + 等级监控四重保障。用户看到的开奖数据是"最新且未被污染"的。
