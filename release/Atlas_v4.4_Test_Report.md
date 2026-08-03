# Atlas v4.4 测试报告（Test Report）

版本：v4.4.0 · 2026-08-04

## 新增测试（tests/v440）

| 文件 | 场景 | 覆盖 |
|------|------|------|
| test_live_draw_v440.py | 33 | 事件总线/日程/check_once 三态/should_check/后台循环 |
| test_background_v440.py | 15 | 计划任务安装/卸载/状态/CLI |
| test_health_v440.py | 44 | 健康等级/年龄/结构/check |
| test_claim_link_v440.py | 31 | 自动兑奖联动/事件触发 |
| test_dashboard_v440.py | 24 | 首页开奖状态卡片 |
| test_matrix_v440.py | 168 | merge 矩阵/合法性/事件/健康/日程 |
| test_matrix2_v440.py | 111 | updater 全流程/异常/后台/兑奖 |
| test_matrix3_v440.py | 433 | 大规模参数化（merge 11×11/限频/写入/健康连续） |
| **合计** | **859（≥800 ✅）** | |

## 覆盖范围（任务书要求）

- 数据更新 ✅（merge 组合/去重/写入格式）
- API 失败 ✅（异常矩阵）
- 网络异常 ✅（静默降级不抛）
- 新期发现 ✅（check_once 五态事件）
- 防旧数据覆盖 ✅（no_new/_valid_remote）
- 后台服务 ✅（计划任务 mock）
- 自动兑奖 ✅（run 矩阵/事件触发）

## 全量回归

| 项 | 数值 |
|----|------|
| v4.4 新增 | **859** |
| 全量回归通过 | **13370** |
| 全量回归失败 | **25（全部存量，零新增）** |

### 失败说明

- **新增失败数量：0**（25 个与 v4.3.1 完全相同，均为 `tests/unit/engine` 统计/ML 算法断言）
- **是否与本版本有关：否**。v4.4 改动模块（live_draw / data_center_v2 / dashboard）无一出现在失败列表中
- **原因**：sklearn 1.9 行为与统计边界的既有技术债（anomaly_detector / calibration / strategy_* 等）

## 关键验证

- 事件总线订阅/发布/多订阅者
- check_once 成功/skipped/failed 三态事件正确
- 健康等级 0-30h 连续单调
- updater 异常静默降级
- worker 真实运行（sync_skipped 无异常）
