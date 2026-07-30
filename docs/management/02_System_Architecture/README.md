# Atlas Quant Platform - 系统架构

> 版本: 1.0
> 状态: 已批准
> 创建日期: 2026-07-28

---

## 1. 架构总览

Atlas Quant Platform 采用严格的分层架构和引擎驱动的设计哲学。

### 1.1 核心架构图 (文本)

`
+----------------------------------------------------------+
|                    UI Layer                                |
|  (CLI / Web Dashboard / Desktop / Notebook)               |
+----------------------------------------------------------+
        |  所有输入输出，永不计算
        v
+----------------------------------------------------------+
|                   API Layer                               |
|   (FastAPI / RPC / IPC)                                   |
+----------------------------------------------------------+
        |  请求路由、校验、认证
        v
+----------------------------------------------------------+
|                 Service Layer                             |
|   (Use Cases / Orchestration / Workflow)                  |
+----------------------------------------------------------+
        |  编排业务逻辑，调用引擎
        v
+----------------------------------------------------------+
|                Engine Layer  (核心)                        |
|  +---------+ +---------+ +---------+ +---------+         |
|  |Analysis | |Backtest | |Simulate | |Optimizer|         |
|  |  Engine | |  Engine | |  Engine | |  Engine |         |
|  +---------+ +---------+ +---------+ +---------+         |
|  +---------+ +---------+ +---------+                     |
|  |Strategy | |Statistic| |  Report |                     |
|  |  Engine | |  Engine | |  Engine |                     |
|  +---------+ +---------+ +---------+                     |
+----------------------------------------------------------+
        |  只调数据层，不下沉业务逻辑
        v
+----------------------------------------------------------+
|                  Data Layer                               |
|   (Repository / Cache / File System)                      |
+----------------------------------------------------------+
        |
        v
+----------------------------------------------------------+
|                 Database                                  |
|   (SQLite / PostgreSQL / Redis)                           |
+----------------------------------------------------------+
`

### 1.2 关键约束

- **AI永远不能直接操作数据库**
- **全部计算必须进入引擎**
- **用户界面永远无法计算**
- **层间只能单向依赖**: UI -> API -> Service -> Engine -> Data -> DB

## 2. 引擎架构 (Engine Layer)

引擎是整个平台的核心。所有数学公式、统计计算、模拟推理都在此完成。

`
engine/
  analysis/     - 统计分析引擎 (频率、遗漏、趋势、分布)
  backtest/     - 回测引擎 (历史数据模拟)
  simulation/   - 模拟引擎 (蒙特卡洛等)
  optimizer/    - 参数优化引擎 (Grid Search, Bayesian)
  strategy/     - 策略引擎 (JSON定义、注册、组合)
  statistics/   - 统计引擎 (假设检验、分布拟合)
  report/       - 报告引擎 (生成PDF/HTML/CSV)
`

### 2.1 引擎设计原则

1. 纯计算：引擎只做计算，不处理IO、不直接访问数据库
2. 无状态：引擎内部不保存状态，状态由上层管理
3. 可测试：每个引擎模块可独立测试，不依赖外部
4. 可组合：引擎之间通过定义好的接口调用
5. 数据驱动：输入输出都是纯数据结构

### 2.2 引擎调用示例

`
Service Layer:
  backtest_service.py
    -> 读取配置
    -> 从Data Layer获取历史数据
    -> 调用 Engine.backtest.runner 执行回测
    -> 从 Engine.backtest.analyzers 获取分析结果
    -> 保存结果到Data Layer
    -> 返回结果

Engine Layer (纯计算，不碰数据库):
  backtest/runner.py
    -> 接收: 历史数据 + 策略JSON + 回测配置
    -> 处理: 逐期模拟交易
    -> 返回: 交易记录列表

  backtest/analyzers.py
    -> 接收: 交易记录列表
    -> 处理: 计算收益率、胜率、最大回撤等
    -> 返回: 性能指标
`

## 3. 插件系统 (Plugin System)

所有领域特定的代码都在插件中。

`
plugins/
  dlt/        - 大乐透插件
  ssq/        - 双色球插件
  kl8/        - 快乐8插件
  football/   - 足球插件 (未来)
`

### 3.1 插件规范

每个插件至少包含:
- plugin.json: 插件元数据
- 数据采集适配器 (继承DataSourceAdapter)
- 号码定义 (号码范围、规则)
- 可选: 内置策略、可视化配置

### 3.2 插件生命周期

`
注册 -> 发现 -> 加载 -> 初始化 -> 运行 -> 卸载
`

### 3.3 插件不包含

插件不包含:
- 业务逻辑 (在Service层)
- 计算逻辑 (在Engine层)
- 数据库操作 (在Data层)

插件只包含:
- 领域特定数据 (号码规则、开奖频率等)
- 数据源适配 (如何采集该彩种的数据)
- 领域特定策略 (预置策略模板)

## 4. 策略系统 (Strategy System)

所有策略都是JSON，不是代码。

### 4.1 策略格式

`json
{
  "strategy_id": "cold_number_tracker",
  "name": "冷号追踪策略",
  "version": 1,
  "rules": [
    {
      "type": "filter",
      "target": "main_numbers",
      "condition": "min_gap",
      "params": {"value": 10}
    },
    {
      "type": "filter",
      "target": "main_numbers",
      "condition": "count",
      "params": {"min": 4, "max": 6}
    }
  ],
  "combinator": "AND",
  "metadata": {
    "author": "system",
    "description": "追踪遗漏超过10期的冷号"
  }
}
`

### 4.2 策略注册

策略存储在后端，通过策略引擎加载和评估。
新增策略不需要修改源码，只需要添加JSON文件。

## 5. AI 集成架构

`
+----------------------------------------------------------+
|                   AI Service Layer                         |
|  +------------------+  +------------------+              |
|  |   LLM Adapters   |  |  Prompt Manager  |              |
|  |  - OpenAI        |  |  - 分析模板      |              |
|  |  - Claude        |  |  - 报告模板      |              |
|  |  - Gemini        |  |  - 策略建议模板  |              |
|  |  - DeepSeek      |  +------------------+              |
|  +------------------+                                     |
+----------------------------------------------------------+
        |
        |  调用引擎获取数据，不直接操作数据库
        v
+----------------------------------------------------------+
|                   Engine Layer                            |
|  (提供结构化数据给AI Service)                              |
+----------------------------------------------------------+
`

### 5.1 AI能力

- 分析建议: 用户输入自然语言需求，AI调用引擎分析并生成结论
- 报告生成: AI自动撰写分析报告 (含图表和数据)
- 策略推荐: AI根据历史数据推荐可能的策略方向
- 异常检测: AI发现数据异常或模式变化

## 6. 数据流

### 采集流
`
数据源 -> Plugin Adapter -> Data Validator -> Engine校验 -> Data Layer -> DB
`

### 分析流
`
UI请求 -> API -> Service -> Engine.analysis -> 返回结果 -> API -> UI
                            (纯计算不碰DB)
`

### 回测流
`
UI请求 -> API -> Service -> Data Layer取历史数据 -> Engine.backtest
                                                        |
                                                   纯计算逻辑
                                                        |
                                                   返回结果 -> Data Layer存储 -> Service -> API -> UI
`

## 7. 技术栈

### 核心
- Python 3.11+
- Poetry 2.0+ (依赖管理)

### Engine
- NumPy, Pandas (数值计算)
- SciPy, StatsModels (统计分析)
- Matplotlib, Plotly (可视化)

### Backend
- FastAPI (Web API)
- SQLAlchemy 2.0 Async (ORM)
- Alembic (数据库迁移)
- Pydantic v2 (校验)

### AI
- OpenAI SDK
- Anthropic SDK
- Google AI SDK

### Infra
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- PostgreSQL / SQLite
- Redis (缓存)
