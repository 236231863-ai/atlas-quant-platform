# Atlas v4.9 P1 真实数据模拟环境

> 阶段：P1 · 用途：在真实用户数据到来前，验证实验管道正确性并建立基准预期
> ⚠️ 诚实声明：本模拟器输出为**合成数据**（基于假设概率），不能替代真实用户数据。

## 一、能力

| 能力 | 方法 | 说明 |
|------|------|------|
| 导入测试用户 | `import_users(ids)` / `import_csv(path)` | 支持批量导入 / CSV（user_id + 行为状态列） |
| 生成用户行为路径 | `generate_path(user, config)` | 按概率生成 7 天行为事件流 |
| 查看留存曲线 | `result["retention"].curve` | D0-D7 逐日留存 |
| 查看漏斗 | `result["funnel"]` | 六阶段转化/流失 |
| 全流程运行 | `run(users, config, experiment_id)` | 生成 + 持久化 + 指标汇总 |
| 导出 | `export_paths(out_dir, result)` | user_paths.csv / user_profiles.csv / validation_metrics.json |

## 二、行为概率配置（SimConfig）

| 参数 | 默认 | 含义 |
|------|-----:|------|
| install_complete | 0.80 | 安装后首次打开 |
| first_save | 0.60 | 保存首张票 |
| reminder_click | 0.40 | 保存后点开奖提醒 |
| claim_check | 0.55 | 提醒后查兑奖 |
| report_view | 0.70 | 兑奖后看报告 |
| daily_open | 0.35 | 每日再打开 |
| premium_view_rate | 0.25 | 打开中看 Premium 页 |
| premium_click_rate | 0.15 | 查看后点付费意愿 |
| days | 7 | 模拟天数 |

## 三、模拟基准输出（100 用户，seed=42）

**漏斗**：安装 100 → 打开 83 → 保存 52 → 提醒 18 → 兑奖 9 → 周报 6
**留存**：D1 47.0% · D3 42.2% · D7 47.0%（满足 Q3 护栏）
**指标**：
- ✅ 安装完成率 Q1 83.0%
- ✅ 首次建档率 Q2 52.0%（≥50%）
- ✅ D1 47.0%（≥40%）· D7 47.0%（≥30%）
- ❌ 提醒点击率 18.0%（<30%，漏斗风险点）
- ✅ 付费意愿 Q4 25.0%（≥5%）

## 四、引擎结构

```text
engine/user_experiment/
├── events.py      # ExperimentTracker（埋点 + 里程碑 + CSV）
├── funnel.py      # ExperimentFunnel（六阶段漏斗）
├── retention.py   # ExperimentRetentionBuilder（D1/D3/D7 曲线）
├── metrics.py     # ValidationMetricsBuilder（Q1-Q4 + WALU）
└── simulator.py   # UserBehaviorSimulator（导入/路径/导出）
```

## 五、使用示例

```python
from engine.user_experiment import UserBehaviorSimulator, SimConfig
sim = UserBehaviorSimulator(seed=42)
users = sim.import_users(["U001", "U002", "U003"])
result = sim.run(users, SimConfig(days=7), experiment_id="exp-A")
print(result["funnel"].to_text())
print(result["retention"].to_text())
print(result["metrics"].to_text())
sim.export_paths("out/", result)
```
