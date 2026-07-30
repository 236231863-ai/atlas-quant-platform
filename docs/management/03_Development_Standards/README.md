# Atlas Quant Platform - 开发规范

> 版本: 1.0
> 创建日期: 2026-07-28

---

## 1. 编码规范

### 1.1 语言与运行时

- Python 3.11+
- UTF-8 编码
- LF 行尾 (Git自动转换)
- 使用 from __future__ import annotations

### 1.2 格式化与Lint

- Black (line-length=88)
- Ruff (启用: F, E, W, I, N, UP, B, SIM, ARG)
- mypy strict mode

### 1.3 命名规范

- 类: PascalCase (DrawResult, BacktestEngine)
- 函数/方法: snake_case (calculate_frequency)
- 常量: UPPER_SNAKE_CASE (MAX_RETRY_COUNT)
- 私有: _前缀 (_validate_internal)
- 接口: ABC后缀 (DataSourceAdapterABC)
- 异常: Exception后缀 (DataNotFoundException)

### 1.4 类型注解

- 所有函数签名必须类型注解
- 优先使用 X | None 而非 Optional[X]
- 优先使用 list[X] 而非 List[X]

### 1.5 Import顺序

1. Python标准库
2. 第三方库
3. 项目内部模块

组间空行分隔。

### 1.6 Docstring

- 公共API必须包含Google风格的docstring
- 参数、返回值、异常都必须有文档
- 单元测试不需要docstring

## 2. Git规范

### 2.1 分支策略

- main: 稳定发布分支
- develop: 开发主线
- feat/xxx: 功能分支
- fix/xxx: 修复分支
- docs/xxx: 文档分支
- refactor/xxx: 重构分支

### 2.2 Commit格式

使用 Conventional Commits:

<type>(<scope>): <description>

类型: feat, fix, docs, refactor, test, chore, perf

### 2.3 PR规范

- 标题格式: [type] 简明描述
- 描述: 背景 + 变更内容 + 测试方式 + 影响范围
- 至少1人review后合并
- 所有CI检查通过
- Squash merge到develop

## 3. 层隔离规范

这是最重要的规范。任何代码必须遵守:

UI Layer -> 只能调用API Layer
API Layer -> 只能调用Service Layer
Service Layer -> 只能调用Engine Layer + Data Layer
Engine Layer -> 纯计算，不碰DB，不碰网络，不碰文件
Data Layer -> 只能访问数据库和文件系统

严禁:
- Engine层导入sqlalchemy或httpx
- Service层直接写计算逻辑 (应该在Engine里)
- API层直接调用Data层
- UI层直接调用Engine

## 4. 引擎开发规范

### 4.1 引擎函数签名

所有引擎函数遵循:

```
def calculate(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    纯计算函数，无副作用。
```

### 4.2 引擎原则

1. 输入输出都是标准Python/NumPy/Pandas类型
2. 不依赖项目其他模块
3. 不读写文件
4. 不发起网络请求
5. 不访问数据库
6. 可独立测试
7. 随机种子由调用方控制

## 5. 插件开发规范

### 5.1 plugin.json 格式

```json
{
  "id": "ssq",
  "name": "双色球",
  "version": "1.0.0",
  "author": "",
  "description": "中国福利彩票双色球插件",
  "entry": "ssq.plugin:SsqPlugin",
  "dependencies": [],
  "engine_version": ">=0.1.0"
}
```

### 5.2 插件接口

每个插件必须实现 PluginABC 接口:
- register(): 注册到系统
- get_lottery_type(): 返回彩种定义
- get_data_source(): 返回数据采集器
- get_builtin_strategies(): 返回内置策略模板

## 6. 测试规范

### 6.1 层级

- 单元测试: 每个引擎模块独立测试 (无外部依赖)
- 集成测试: Service + Data Layer协同测试
- E2E测试: 完整工作流测试

### 6.2 覆盖率目标

- Engine模块: >= 90%
- Service模块: >= 80%
- 项目整体: >= 80%

### 6.3 测试原则

- Engine测试: Mock Data Layer, 只测计算逻辑
- Service测试: Mock Engine和Data, 只测编排逻辑
- API测试: 通过TestClient测端点
- 所有外部IO在测试中必须Mock
