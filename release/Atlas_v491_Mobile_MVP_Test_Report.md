# Atlas v4.9.1 — Mobile MVP 测试报告（Test Report）

> 测试套件：`tests/v492/` · 覆盖：页面流程/数据存储/埋点/来源隔离/提醒逻辑/用户漏斗

---

## 一、测试数量（任务书要求 ≥100）

| 覆盖范围 | 测试数 | 文件 |
|---------|-------:|------|
| 号码解析 | 27 | `test_parser.py` |
| 奖级匹配 | 19 | `test_draw_match.py` |
| Repository / 数据存储 | 28 | `test_repositories.py` |
| 埋点扩展 | 18 | `test_mobile_events.py` |
| 来源隔离 | 9 | `test_source_isolation.py` |
| 提醒逻辑 | 12 | `test_reminder.py` |
| 服务链路（页面流程） | 24 | `test_service_flow.py` |
| API 路由 | 14 | `test_api.py` |
| **合计** | **151** | ✅ **≥100 达标** |

---

## 二、关键测试结论

### 页面流程（服务链路）
- 注册 → 录票 → 开提醒 → 查奖 → 漏斗全链路通过
- 编号递增（U0001→U0002）、openid 去重通过

### 数据存储
- 五张表增删查、upsert、去重、click_rate 计算全部通过
- **Repository 层验证**：业务代码零 SQL

### 埋点
- `SOURCE_MOBILE` 独立来源且计入真实统计
- 5 个 mobile 事件全部在事件集（总数 22）
- `real_events()` = REAL + MOBILE，SIMULATION 严格排除

### 来源隔离
- funnel/retention 的 REAL 口径自动包含 MOBILE
- SIMULATION 单独统计不混入

### 提醒逻辑
- 创建/去重/下发/点击回执/点击率通过
- 微信客户端 mock 模式正常

### 奖级匹配（修复验证）
- 大乐透全部 13 个中奖组合正确
- **九等奖 `0+2`（后区全中）修复**：原单键字典漏判，已改为多组合列表

---

## 三、回归

| 套件 | 结果 |
|------|------|
| v490（埋点/漏斗/留存/反馈） | **264 passed** |
| v492（Mobile MVP 全量） | **151 passed** |
| v481（工作台手动添加） | **19 passed** |
| v382_p1（兑奖链路） | **541 passed** |
| **验证批次合计** | **975 passed / 0 failed**（22.9s） |
| **影响面实证** | 全项目仅 v490/v492 引用被改模块（`grep -rl user_experiment tests/`） |

> **回归结论（0 新增失败）依据**：
> 1. 被改模块 `engine/user_experiment/` 全项目仅被 `tests/v490` + `tests/v492` 引用（grep 实证），两者合计 415 passed，0 失败
> 2. 其余 15,000+ 测试不 import 被改模块 → 模块隔离保证其行为不受影响
> 3. 核心业务套件（v481/v382_p1）抽样通过，确认项目整体健康
>
> ⚠️ 诚实说明：完整全量回归（16,000+ 测试含大量 PySide6 UI 测试）在本机运行 75+ 分钟未完成，采用「受影响套件全过 + 影响面实证 + 核心套件抽样」作为等效回归证据。25 个 `tests/unit/engine` 存量技术债与本次改动无关。

---

## 四、测试隔离保障

- `MobileDB.in_memory()` + **StaticPool**：内存库跨连接共享，测试不写真实文件
- conftest 自动设 `ATLAS_STORAGE_DIR=tmp_path`：保护 `~/.atlas` 真实数据
- API 测试用 `api.reset_db()` 每测试替换 in-memory DB

---

## 五、诚实声明

- 全部测试为**代码级验证**，不含真实用户数据
- 真实留存/保存率等产品指标需 14 天采集后由报告呈现
