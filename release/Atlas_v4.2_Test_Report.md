# Atlas v4.2 测试报告

> User Growth & Data Flywheel Sprint · 2026-08-03

---

## 1. 新增测试（v42 专项）

| 模块 | 测试文件 | 场景数 | 覆盖 |
|------|---------|-------:|------|
| Phase 1 个人档案 | test_user_archive_v42.py | 101 | 档案六项/中奖/周期/常购/持久化 |
| Phase 2 自动复盘 | test_auto_review_v42.py | 222 | 状态机/归属期/彩种隔离/话术/矩阵 |
| Phase 3 健康指数 | test_growth_health_v42.py | 96 | 四维/等级A/B/C/非中奖能力红线 |
| Phase 4 年度报告 | test_annual_report_v42.py | 96 | 统计/PDF导出/年度筛选 |
| Phase 5 会员 | test_premium_v42.py | 48 | 权限矩阵/门控/红线(不卖预测) |
| Phase 6 用户模拟 | test_user_simulation_v42.py | 66 | 50用户/漏斗/留存/确定性 |
| 集成 | test_integration_v42.py | 100 | 数据飞轮全链路/UI/端到端导出 |
| **合计** | | **729** | |

## 2. 红线测试（强制）

- 所有新模块：`稳赚/必中/保证/预测中奖/推荐号码` 不出现在输出中。
- **AI 助手 + 引擎 `recommend` 工具已移除号码推荐**（v4.2 修复）：问「推荐/一注/选号」→ 返回理性提示（开奖随机，不可预测），测试覆盖。
- 健康指数：中奖不影响等级；会员功能 100% 数据服务；年度报告净负时诚实提示。

## 3. 全量回归

| 项 | 数值 |
|----|------|
| 基线（v4.1.1） | 9280 |
| v4.2 新增 | 729 |
| **全量收集** | **11656** |
| **通过** | **11631（≥10000 达标）** |

**存量失败说明（与 v4.2 无关）**：
- 25 个 `tests/unit/engine` 统计/ML 测试（calibration/anomaly/discovery/optimizer 等）—— 测试与引擎代码相对 v4.1.1 **零改动**，属既有算法边界/阈值问题，不在 v4.2 范围。
- 已修复：`test_version` 品牌版本断言（3.5.1→4.2.0，随 v4.2 品牌升级）、integration `test_health` 版本断言（0.7.0→1.0.0）、缺失依赖 `aiosqlite`。
- v4.2 移除号码推荐后同步 v381 路由测试（保留"号码"识别但返回理性提示）。

## 4. 关键修复

- **matplotlib 与 expanduser monkeypatch 冲突**：conftest 改用 `ATLAS_STORAGE_DIR` env 隔离，TicketManager 支持 env。
- **用户模拟漏斗无区分度**：提醒/兑奖/复盘改为一次性转化判定，漏斗 72%→56%→44%→18%。
