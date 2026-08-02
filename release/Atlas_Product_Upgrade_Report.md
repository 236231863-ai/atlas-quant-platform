# Atlas Product Upgrade Report — v3.6.1

> Sprint: v3.6.1 Product Trust & Real Usage Upgrade
> 日期：2026-08-02
> 结论：**Atlas 已从「开发 Demo」升级为「可信分析工具」** —— 数据真实、回测诚实、结果可带走、运行稳定。

---

## 1. 升级总览

| 维度 | v3.6.0 | v3.6.1 | 状态 |
|------|--------|--------|------|
| 数据 | 15 期样例 | **520 期官方真实数据**（2023-02 ~ 2026-08） | ✅ |
| 数据可信度 | 无提示 | **可信等级 A + 数据不足警告** | ✅ |
| 回测 | 全量拟合、无对照 | **样本内外划分 + 随机基准对照 + 免责声明** | ✅ |
| 首次使用 | 问"你叫什么名字" | **三步引导（用途→数据→模式），30 秒上手** | ✅ |
| 结果导出 | 不可保存 | **MD / CSV / PNG / PDF 四格式导出** | ✅ |
| 稳定性 | 无兜底 | **全局异常 + 崩溃恢复 + 日志 + 健康检查** | ✅ |
| 测试 | 25 个已知失败 | **859 个工程测试全过** | ✅ |
| 发布 | Atlas_Setup.exe | **AtlasQuant-3.6.1-Setup.exe + Portable zip** | ✅ |

---

## 2. 各 Phase 交付明细

### Phase 0 产品冻结 + 模块审计
- 交付：`docs/audit/Atlas_Module_Usage_Report.md`
- 结论：desktop（1522 行）是唯一用户入口；engine 209 文件仅 5 目录被产品代码引用；~110 概念模块冻结归档；`api_client.py` 死代码标记删除。
- 冻结：v3.6.1 仅触碰 desktop 5 处 + 3 个新 engine 子包。

### Phase 1 数据真实性升级
- 新增 `engine/data_center_v2/`：`DataSourceManager`（CSV/Excel/API/Database 四源）+ `DataQualityReport`（数量/时间/完整率/可信等级 A-D）。
- **抓取 520 期大乐透官方真实数据**（体彩 webapi.sporttery.cn），`data/raw/dlt_history.csv`。
- 桌面 `data_loader.py` 升级：统一 numbers 格式解析、history 优先。
- Dashboard 显示「数据来源 + 可信等级 + 不足警告」。

### Phase 2 回测可信化
- 新增 `engine/evaluation_v2/`：`temporal_split`（70/30 时序划分）、`RandomBaseline`（随机选号基准）、`PerformanceReport`（样本内外 ROI / 超额 / 结论）、`disclaimer`（禁用诱导词）。
- 回测页显示：样本内外 ROI、随机基准 90% 区间、诚实结论、免责声明。
- 策略页增加随机性声明。

### Phase 3 用户体验升级
- `first_run_dialog.py` 重写为三步引导（用途选择 → 数据选择 → 分析模式）。
- 主窗口按引导结果跳转目标页，30 秒完成第一次分析。

### Phase 4 输出系统
- 新增 `engine/export/`：Markdown / CSV / PNG / PDF 四格式（fpdf2 + 中文字体）。
- 报告页：导出 MD/PDF/CSV；回测页：明细 CSV / 报告 PDF / 图表 PNG。

### Phase 5 产品稳定性
- 新增 `desktop/health.py`：全局异常 hook、崩溃标记与恢复提示、日志落盘与导出、启动健康检查。
- `main.py` 集成；崩溃后下次启动弹恢复提示。

### Phase 6 发布工程
- `AtlasQuant-3.6.1-Setup.exe`（156 MB，Inno Setup 双语）
- `AtlasQuant-3.6.1.zip`（154 MB，Portable）

---

## 3. 测试验收（859 项全过）

| 覆盖域 | 测试数 | 关键断言 |
|--------|--------|----------|
| 数据层 data_center | ~110 | 可信等级阈值、完整率、四源加载、号码解析 |
| 回测 evaluation | ~130 | 样本划分、随机基准、性能报告、免责禁用词 |
| 导出 export | ~60 | MD/CSV/PNG/PDF 生成与内容 |
| UI 流程 | ~90 | 6 页实例化、引导步骤、质量标签、崩溃恢复 |
| 安装/发布 | ~70 | setup.iss / spec / 版本 / requirements / 数据文件 |
| 边界矩阵 | ~400 | 号码组合、统计边界、回测网格、斐波那契序列 |

---

## 4. 已知事项

- 双色球数据：当前仅样例（15 期），官方体彩 API 仅覆盖体彩游戏（大乐透），福彩双色球接入待 `tools/fetch_lottery_data.py` 扩展福彩数据源。
- engine 旧概念模块（~110 目录）已冻结，尚未物理移入 `engine/archive/`（已列入 v3.7）。
- PDF 导出依赖系统中文（微软雅黑），打包机需含中文字体。

---

*本报告基于 2026-08-02 实测（UI 树验证 520 期数据与可信等级 A、859 测试通过、双产物生成）。*
