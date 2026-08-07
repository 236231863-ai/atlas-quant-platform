# Atlas v4.9 P2 架构报告（首次体验 + 数据可靠性 + 移动端预研）

> 阶段：P2 · 关注架构合理性，非功能堆积

## 一、改动模块

| 模块 | 改动 | 架构意义 |
|------|------|---------|
| `desktop/pages/first_run_dialog.py` | 三步引导重构为**建档导向** | 首次价值理解前置，研究指标从首屏移除 |
| `desktop/windows/main_window.py` | 首次引导后跳转**工作台** | 引导闭环到建档入口 |
| `desktop/pages/dashboard_page.py` | 开奖状态卡强化 🟢/🟡/🔴 | 数据可信状态诚实可见 |
| `tests/v490/test_p2_experience.py` | 新增 29 项 P2 测试 | 首次体验/号码解析/数据可信/安全覆盖 |

## 二、数据架构（审计结论）

```
DataSource ──► Updater ──► Cache ──► DataLoader ──► PrizeCalculator ──► UI
  (API)        (合并/校验)   (用户缓存)  (缓存优先)      (兑奖)          (状态卡)
```

**可靠性设计（保持）**：
1. `_valid_remote` 号码范围校验（dlt 5+2/1-35/1-12；ssq 6+1/1-33/1-16）
2. `no_new` 无新增期号不写缓存
3. `should_update` 24h 限频
4. 静默降级（API 异常/空源保留本地）
5. UI 分级显示（A 绿/B/C 黄/D 红）+ 来源/时间/期号

**待优化**：
- 双色球数据源（gameNo=235 返回 0）
- 后台计划任务需主动安装

## 三、首次体验架构

```
首次启动
  → FirstRunDialog（3 步价值引导，无研究指标）
  → 跳转工作台（建档入口）
  → 手动添加面板（复用 TextImporter + TicketParser）
  → 保存成功 → 表格显示购买/开奖日期（自动填充）
```

**号码解析复用**：`TicketParser` 唯一解析系统，无冲突实现。

## 四、移动端架构预研（详见 Mobile_Feasibility_Report）

推荐：**Windows 桌面端 + 本地/云 API + 手机 Web**（方案 B，总分 39/45）
- 复用 FastAPI 后端 + 数据引擎
- 需新增：账号体系 + 票据云端同步 + 推送

## 五、架构健康度

| 维度 | 评价 |
|------|------|
| 复用性 | ✅ 复用 TicketParser/TextImporter/DataHealth/IncrementalUpdater |
| 可扩展性 | ✅ 数据源/UI 状态分层清晰，双色球源可替换 |
| 诚实性 | ✅ 数据状态不伪装实时 |
| 遗留债务 | 双色球实时源、云同步、后台任务主动安装 |
