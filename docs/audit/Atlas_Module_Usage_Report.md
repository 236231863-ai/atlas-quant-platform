# Atlas Module Usage Report

> Sprint: v3.6.1 Phase 0（产品冻结 / 模块使用审计）
> 日期：2026-08-02
> 方法：代码库全量扫描（文件规模 / grep 引用关系 / 测试覆盖 / 产品入口实证）
> 目的：冻结现有 37 Sprint 代码，分类 KEEP / IMPROVE / ARCHIVE / DELETE，为 v3.6.1 升级划定边界。

---

## 1. 代码库规模统计

| 区域 | 文件数 | 代码行 | 进入产品流程？ |
|------|--------|--------|----------------|
| `desktop/` | 16 | 1,522 | ✅ **唯一用户入口**（6 页面 + 数据层 + 档案） |
| `backend/` | 37 | 1,463 | ⚠️ 有实现，无外部调用方 |
| `engine/` | 209 | 9,933 | ⚠️ 仅 5 目录被产品代码引用 |
| `core/` | 13 | 744 | ✅ 被 backend 使用（errors/types/validation） |
| `frontend/src/` | 10 | 107 | ❌ 骨架，未构建发布 |
| 顶层概念 md | 67 | — | ❌ 存档性质 |

**关键失衡**：用户实际触达的 `desktop/` 仅 1,522 行，而 `engine/` 有 9,933 行且 95% 与产品脱节。

---

## 2. 调用关系分析（实证）

### 2.1 产品代码 → engine 的引用（全库 grep）

**desktop 引用 engine = 0**（桌面完全独立，自带 `stats.py`/`data_loader.py`）
**tools 引用 engine = 0**
**backend 引用 engine = 3 个文件**（仅 `api/action`、`api/decision`、`api/operation`）

被产品代码引用的 engine 目录（**仅 5 个**）：

| engine 目录 | 引用方 | 用途 |
|-------------|--------|------|
| `action` | backend/api/action | 动作层 |
| `decision` | backend/api/decision | 决策层 |
| `evaluation` | backend/api/operation | 评估 |
| `observability` | backend/api/operation | 可观测 |
| `autonomous_maintenance` | backend/api/action | 自维护 |

### 2.2 测试对 engine 的覆盖

- 92 个测试文件引用 engine（覆盖 107/120 个目录）
- **注意**：「被测试引用」≠「进入产品流程」——大量概念模块只有测试、无任何用户入口。

### 2.3 后端被调用情况

- 桌面侧唯一引用 `api_client.py`（**0 处调用，死代码**）
- frontend 侧 `client.ts`（骨架，未构建）

---

## 3. 分类结果

### ✅ KEEP（进入产品流程，保留）

| 资产 | 理由 |
|------|------|
| `desktop/` 全部 16 文件 | 唯一用户入口，6 页面真实可用 |
| `core/`（errors/types/validation/events） | 被 backend 使用，基础可靠 |
| `backend/service/` + `api/v1/` | 真实实现 + 未来 Web 的基础 |
| `engine/action, decision, evaluation, observability, autonomous_maintenance` | 被 backend 引用 |
| `engine/backtest, statistics, probability, features, analysis` | 核心算法资产、测试覆盖充分，v3.6.1 将重构进产品（Phase 2 复用） |

### 🔧 IMPROVE（v3.6.1 升级对象）

| 现有资产 | 升级为 |
|----------|--------|
| `desktop/data_loader.py` | `engine/data_center_v2/`（Phase 1：多源 + 质量报告） |
| `desktop/pages/backtest_page.py` | `engine/evaluation_v2/`（Phase 2：样本划分 + 随机基准） |
| `desktop/pages/first_run_dialog.py` | 首次流程重构（Phase 3） |
| `desktop/pages/reports_page.py` + `analysis_page.py` | `engine/export/`（Phase 4：PDF/MD/CSV/PNG） |
| `desktop/main.py` | 稳定性加固（Phase 5：全局异常/崩溃恢复/日志） |

### 📦 ARCHIVE（有测试但无产品入口，冻结归档）

以下 engine 概念模块**保留代码、冻结开发、移入 `engine/archive/`**（README 声明"实验性模块"），不再投入：

- `agent_*`：agent_economy, agent_market, agent_personality, agent_protocol, agents
- `ecosystem_*`：ecosystem_governance, ecosystem_intelligence, ecosystem_operation, ecosystem_reputation, ecosystem_strategy
- `autonomous_*`：autonomous_growth（maintenance 保留）
- `industry_*`：industry_agents, industry_knowledge, industry_report, industry_template, industry_workflow
- `knowledge_*`：knowledge, knowledge_exchange, knowledge_fusion, knowledge_transfer
- 其他概念：license_economy, publication, global_network, research_marketplace, research_competition, expert_council, expert_network, review_committee, commercial_service, enterprise_success, distributed, collaboration, debate, commerce, institution, memory, meta_learning, personal_ai 等

> 统计：约 **110 个目录**（engine 120 目录中除 KEEP 5 + IMPROVE 相关 + 边界外），合计 ~5,000+ 行。

### 🗑 DELETE（完全死代码）

| 资产 | 证据 |
|------|------|
| `desktop/api_client.py`（17 行） | 全库 0 引用 |
| `frontend/src/`（107 行 TS） | 骨架，未构建、未发布、无产品入口 |

---

## 4. 用户价值 × 是否进入产品流程矩阵

| 模块 | 用户价值 | 进入产品流程 | 结论 |
|------|----------|--------------|------|
| Desktop 6 页面 | ⭐⭐⭐⭐ | ✅ | KEEP / IMPROVE |
| engine/backtest 等核心算法 | ⭐⭐⭐（潜在） | ❌ 未接入 | 重构进产品（Phase 2） |
| backend 13 路由 | ⭐⭐（潜在） | ❌ | KEEP（备用） |
| engine 概念模块（~110） | ⭐（无） | ❌ | ARCHIVE |
| frontend 骨架 / api_client | ⭐（无） | ❌ | DELETE |

---

## 5. Phase 0 冻结结论

1. **v3.6.1 改动边界**：仅触碰 IMPROVE 列表（desktop 5 处）+ 新增 3 个 engine 子包（data_center_v2 / evaluation_v2 / export）。
2. **冻结对象**：ARCHIVE 的 ~110 个概念模块**禁止继续开发**；DELETE 项立即移除。
3. **版本**：v3.6.0 → v3.6.1，保持「可安装、可运行、可发布」红线。

---

*本报告由代码库全量扫描生成（文件数 / grep 引用 / 测试覆盖 / 产品入口实证），非人工估测。*
