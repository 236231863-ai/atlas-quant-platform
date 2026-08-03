# Atlas v4.3 测试报告（Test Report）

版本：v4.3.0 · 2026-08-03

## 新增测试（tests/v43）

| Phase | 文件 | 场景 | 要求 |
|-------|------|------|------|
| P1 真开奖提醒 | test_reminder_v43.py | 153 | ≥150 ✅ |
| P2 自动兑奖中心 | test_claim_center_v43.py + test_claim_matrix_v43.py | 299 | ≥200 ✅ |
| P3 彩票资产中心 | test_asset_center_v43.py + test_asset_matrix_v43.py | 181 | ≥150 ✅ |
| P4 用户成长系统 | test_growth_system_v43.py | 101 | ≥100 ✅ |
| P5 首页重构 | test_dashboard_p5_v43.py + test_dashboard_p5_matrix.py | 112 | ≥100 ✅ |
| **合计** | | **846** | **≥800 ✅** |

## 覆盖范围

- 提醒：倒计时 / 桌面通知 / 提醒事件 / 状态机 / 边界
- 兑奖：4 状态判定 / 待兑奖列表 / 自动兑奖 / 事件记录 / 持久化 / 端到端
- 资产：中奖率 / 净收益 / 亏损率 / 风险等级 / 年度报告 / 成本矩阵
- 成长：连续周数（跨年/中断/同周）/ 等级阈值 / 年度 Atlas Report
- 首页：3 秒价值指标 / 无研究指标 / 动态话术 / 引导

## 全量回归

| 项 | 数值 |
|----|------|
| v4.3 新增 | **846** |
| 全量回归通过 | **12477** |
| 全量回归失败 | **25**（全部为存量技术债，见下） |

### 失败说明（任务书要求：新增失败数量 / 失败原因 / 是否与本版本有关）

- **新增失败数量：0**（25 个失败与 v4.2 回归的 25 个完全相同）
- **失败原因**：`tests/unit/engine` 统计/ML 算法断言（anomaly_detector / calibration / discovery / intelligence_integration / product_intelligence / strategy_* 等），属 sklearn 1.9 行为与统计边界的既有技术债
- **是否与本版本有关：否**。v4.3 改动模块（reminder_center / claim_center / asset_center / growth_system / user_events / dashboard / profile / main_window）无一出现在失败列表中；这些测试相对 v4.1.1 起即失败，非本次引入

## 关键修复验证

| 修复 | 验证 |
|------|------|
| `TicketRecord.claimed` 持久化 | ✅ set_claimed 跨实例重载测试 |
| `ClaimCenter.summary_text` ticket_id | ✅ auto_claim to_dict/summary 测试 |
| 资产中心活跃月切片 | ✅ 多月活跃测试 |
| 首页研究指标移除 | ✅ 断言不含「平均和值/奇偶/88.1」 |
