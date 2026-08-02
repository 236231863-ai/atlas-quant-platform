# Phase 3 — 真实数据体系报告

> Atlas Quant Platform v3.6.0 Product Launch
> 日期：2026-08-02

---

## 完成报告

### 数据体系架构

```
用户真实数据（用户导入 CSV）→ 用户数据目录 data/raw/<lottery>_user_data.csv
                                        ↓ 优先加载
项目数据（data/raw/*.csv）───────────────┤
                                        ↓ 回退
内置演示数据（打包进 exe）──────────────→ 明确标注「演示数据」
```

### 交付内容

| 项目 | 路径 | 说明 |
|------|------|------|
| 多彩种数据层 | `desktop/data_loader.py` | dlt/ssq 双彩种，用户数据优先 |
| 数据导入工具 | `tools/import_data.py` | 校验并导入用户真实 CSV |
| 数据来源信息 | `desktop/data_loader.get_data_source()` | 来源/期数/说明 |
| Dashboard 来源显示 | `desktop/pages/dashboard_page.py` | 界面标注数据来源 |
| SSQ 演示数据 | `data/raw/ssq_2024_sample.csv` | 双色球 15 期（真实规则模拟） |

### 用户数据导入流程

```bash
# 用户将真实开奖数据导出为 CSV（可从官方开奖网站/第三方数据服务获取）
python tools/import_data.py my_dlt_data.csv --lottery dlt
```

导入后桌面端自动优先加载用户真实数据，Dashboard 标注「用户导入数据」。

## 测试报告

| 测试项 | 结果 |
|--------|------|
| dlt 数据加载 | ✅ 15 期（演示） |
| ssq 数据加载 | ✅ 15 期（演示，33红6+16蓝规则） |
| 用户数据优先 | ✅ 存在 `<lottery>_user_data.csv` 时优先 |
| 数据来源标注 | ✅ 演示/用户来源清晰 |
| Dashboard 集成 | ✅ 来源显示正常 |
| 导入工具校验 | ✅ 格式/期数/号码范围校验 |

## 使用说明（用户角度）

### 1. 用户在哪里下载？
数据导入工具随项目提供（`tools/import_data.py`）；正式发布时可在桌面「数据」入口触发。

### 2. 用户如何安装？
无需安装。将真实开奖 CSV 放入 `data/raw/` 或使用导入工具。

### 3. 用户如何第一次使用？
默认内置演示数据可立即体验；想用真实数据：导入 CSV → 重启桌面 → 自动加载。

### 4. 用户获得什么价值？
- 真实开奖数据支撑的分析结果才有实际意义
- 数据来源透明（用户/演示一目了然）
- 多彩种扩展（大乐透/双色球）

## 实际产物

```
desktop/data_loader.py      多彩种数据层（用户优先）
tools/import_data.py        数据导入工具
data/raw/ssq_2024_sample.csv  双色球演示数据
Dashboard 数据来源显示
```
