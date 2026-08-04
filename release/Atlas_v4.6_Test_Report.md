# Atlas v4.6 测试报告（Test Report）

版本：v4.6.0 · 2026-08-04

## 新增测试（tests/v460）

| 文件 | 场景 | 覆盖 |
|------|------|------|
| test_analytics_v460.py | 51 | 8事件格式/追踪/漏斗/留存 |
| test_reminder_schedule_v460.py | 26 | 24h/3h/开奖后提醒/去重 |
| test_onboarding_v460.py | 20 | 引导价值导向/onboarding 事件 |
| test_claim_summary_v460.py | 25 | 首页兑奖汇总/状态机 |
| test_monthly_v460.py | 40 | 月度复盘/诚实负期望 |
| test_premium_v460.py | 23 | Premium Feature/解锁提示/埋点 |
| test_matrix_v460.py | 305 | analytics/funnel/retention/premium/monthly 矩阵 |
| test_matrix2_v460.py | 122 | reminder/claim/analytics 深度矩阵 |
| test_matrix3_v460.py | 464 | 纯计算参数化矩阵 |
| **合计** | **1076（≥1000 ✅）** | |

## 覆盖范围（任务书要求）

- **用户事件** ✅（8 事件 + premium 事件，格式/追踪/矩阵）
- **后台提醒** ✅（24h/3h/开奖后 + 去重 + 计划）
- **首次启动** ✅（价值引导 + onboarding start/complete/drop）
- **兑奖流程** ✅（首页汇总 + 状态机 + 中奖匹配）
- **资产中心** ✅（月度复盘 + 净收益 + 诚实）
- **商业化入口** ✅（Premium Feature + premium_view/click）

## 全量回归

| 项 | 数值 |
|----|------|
| v4.6 新增 | **1076** |
| 全量回归通过 | **14725** |
| 全量回归失败 | **25（全部存量，零新增）** |

### 失败说明

- **新增失败数量：0**（25 个与 v4.5 完全相同，均为 `tests/unit/engine` 统计/ML 算法断言）
- **是否与本版本有关：否**。v4.6 改动模块（user_analytics / draw_monitor / asset_center / premium / dashboard / first_run）无一出现在失败列表中
- **原因**：sklearn 1.9 行为与统计边界的既有技术债

## 关键验证

- 漏斗转化/流失正确（同 user 去重）
- Retention D1/D3/D7 计算正确
- 提醒计划按时段（pre_24h/pre_3h/after_draw）
- 月度净收益 = 中奖 - 投入（负期望诚实）
- premium 埋点记录

## 已知限制

- 提醒/支付的实际触发依赖 Windows 环境（测试验证计划与命令逻辑）
