# Phase 1 Review — 用户实验系统（v4.9 P1）

> 阶段：P1 · 状态：**通过，待确认进入 P2**
> 范围：严格围绕「真实用户行为验证」，未新增娱乐/预测/无验证功能

## 一、交付内容

| 交付 | 文件 | 状态 |
|------|------|------|
| 用户实验系统引擎 | `engine/user_experiment/`（events/funnel/retention/metrics/simulator） | ✅ |
| 用户行为埋点报告 | `release/Atlas_v4.9_P1_Behavior_Event_Report.md` | ✅ |
| 用户漏斗报告 | `release/Atlas_v4.9_P1_User_Funnel_Report.md` | ✅ |
| 真实数据模拟环境说明 | `release/Atlas_v4.9_P1_Simulation_Environment.md` | ✅ |
| 产品验证报告（Q1-Q4） | `release/Atlas_v4.9_P1_User_Validation_Report.md` | ✅ |

## 二、Q1-Q4 验收口径（已实现）

| 指标 | 定义 | 目标 | 引擎 |
|------|------|------|------|
| Q1 安装完成率 | install 后至少打开一次 / 安装 | ≥50% | `metrics.py` |
| Q2 首次建档率 | 保存首张票 / 安装 | **≥50%** | `metrics.py` |
| Q3 D1 / D7 留存 | 首见后第 1 / 7 天活跃 | **≥40% / ≥30%** | `retention.py` |
| Q4 付费意愿 | premium_click / premium_view | ≥5% | `metrics.py` |
| 北极星 WALU | 本周有彩票行为（保存/兑奖/提醒点击）用户 | — | `metrics.py` |

## 三、测试证明

- `tests/v490/` 新增 **155 个测试**（≥100 达标）
- 覆盖：事件记录/里程碑/CSV 导出/漏斗/留存曲线/Q1-Q4 指标/模拟器（导入/路径生成/导出/seed 可复现）
- **155 passed**，零失败

## 四、产品价值

1. **行为埋点真实化**：7 类事件（install/open/saved/reminder_clicked/claim_checked/report_viewed/premium_view）+ 里程碑，CSV 可导出——首次具备「回答用户为什么打开」的数据管道
2. **漏斗真实化**：安装→首次打开→保存→提醒→兑奖→周报六阶段，每阶段用户数/转化率/流失率
3. **留存曲线真实化**：D1/D3/D7 + 逐日曲线，直接对账 Q3 护栏
4. **模拟环境**：可导入测试用户（CSV）、生成行为路径、查看留存曲线——真实用户到来前先验证管道正确性

## 五、已知限制（诚实声明）

- 模拟器输出为**合成数据**（基于假设概率），用于验证实验管道，**不能替代真实用户数据**
- 埋点数据当前仅本地 jsonl，未接入 UI 仪表盘（P4 交付）
- 提醒点击率模拟值 18% 低于 30% 目标——暴露真实漏斗风险点，非缺陷

## 六、结论

P1 完成「真实用户验证」的数据采集与计算管道。**建议通过，进入 P2（新用户体验优化）**。
