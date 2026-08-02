# Atlas 产品数据分析报告（v3.7.1）

> 说明：v3.7.1 起启用产品使用事件采集。本报告描述采集能力与预期指标，Beta 期间数据将据此汇总。

---

## 1. 事件体系

| 事件 | 含义 | 用途 |
|------|------|------|
| app_open | 应用启动 | 会话数、DAU |
| app_close | 应用关闭 | 会话时长、崩溃率 |
| analysis_start | 开始分析 | 分析漏斗起点 |
| analysis_complete | 完成分析 | 完成率 |
| report_export | 导出报告 | 导出活跃度 |
| backtest_run | 运行回测 | 回测使用度 |
| strategy_view | 查看策略 | 策略偏好 |

## 2. 输出指标（ProductUsageReport）

| 指标 | 公式 | 意义 |
|------|------|------|
| total_sessions | max(app_open, app_close) | 使用频次 |
| analysis_completion_rate | complete / start | 分析完成度 |
| crash_rate | (open - close) / open | 稳定性（越低越好） |
| active_days | 去重日期数 | 留存 |
| export_formats | 各格式计数 | 导出偏好 |
| top_strategies | 策略频次 | 功能偏好 |

## 3. Beta 预期基线

| 指标 | 目标 |
|------|------|
| 会话数 | Beta 1 ≥ 100 |
| 分析完成率 | ≥ 70% |
| 崩溃率 | < 5% |
| 活跃天数（单用户） | ≥ 3 天/周 |

## 4. 数据流

```
用户操作 → ProductAnalytics.track() → ~/.atlas/analytics.jsonl
    → build_usage_report() → ProductUsageReport → 周报
```

## 5. 隐私

- 所有数据仅存本机（~/.atlas/analytics.jsonl）。
- 不采集：账号、号码选择、个人信息。
- Beta 结束后可提供"清除数据"入口。

## 6. 示例报告结构

```
📊 Atlas 产品使用报告
· 会话：120 次，活跃天数 21
· 分析：启动 98 / 完成 76（完成率 78%）
· 导出 45 次 · 回测 30 次 · 策略查看 52 次
· 崩溃率（open 无 close）：3%
· 导出格式：pdf:20, md:15, csv:8, png:2
· 热门策略：hot(25), cold(15), balanced(12)
```
