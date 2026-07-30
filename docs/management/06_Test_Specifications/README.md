# Atlas Quant Platform - 测试规范

> 版本: 1.0
> 创建日期: 2026-07-28

---

## 1. 测试策略

### 1.1 测试金字塔

- 单元测试 (70%): Engine层 + Core层, 无外部依赖
- 集成测试 (20%): Service层 + Data层, 需要数据库
- E2E测试 (10%): 完整工作流, 全栈

### 1.2 测试工具

- pytest 8.0+
- pytest-asyncio (异步测试)
- pytest-cov (覆盖率)
- pytest-mock (Mock)
- pytest-benchmark (性能基准)

### 1.3 测试标记

- unit: 单元测试, 无外部依赖
- integration: 集成测试, 需要数据库
- e2e: 端到端测试
- slow: 超过5秒的测试

## 2. 单元测试 (Engine层)

### 2.1 测试范围

- 所有分析函数
- 所有回测逻辑
- 所有策略评估逻辑
- 所有统计计算
- 值对象的不变式

### 2.2 不测试的内容

- 数据库操作 (集成测试)
- 网络请求 (Mock)
- 文件IO (Mock)
- 框架行为

### 2.3 引擎测试示例

```python
def test_calculate_frequency_with_sample_data():
    data = pd.DataFrame({
        "number": [1, 2, 3, 1, 2, 1]
    })
    result = calculate_frequency(data, ["main_numbers"])
    assert result[1] == 3
    assert result[2] == 2
    assert result[3] == 1

def test_calculate_frequency_with_empty_data():
    data = pd.DataFrame({"number": []})
    result = calculate_frequency(data, ["main_numbers"])
    assert len(result) == 0
```

## 3. 集成测试 (Service层)

### 3.1 测试范围

- Service层编排逻辑
- Data层Repository实现
- 数据库迁移 (正向+回滚)

### 3.2 示例

```python
@pytest.mark.integration
async def test_save_and_retrieve_draw(db_session):
    repo = SqlAlchemyDrawRepository(db_session)
    draw = create_sample_draw()
    saved = await repo.save(draw)
    found = await repo.find_by_id(saved.id)
    assert found is not None
```

## 4. E2E测试

### 4.1 测试范围

- CLI完整工作流
- API端点端到端

### 4.2 示例

```python
@pytest.mark.e2e
def test_cli_collect_then_analyze(cli_runner):
    result = cli_runner.invoke(collect_cmd, ["ssq", "--draws", "10"])
    assert result.exit_code == 0
    result = cli_runner.invoke(analyze_cmd, ["ssq", "frequency"])
    assert result.exit_code == 0
```

## 5. 覆盖率目标

- engine/analysis: >= 90%
- engine/backtest: >= 90%
- engine/strategy: >= 90%
- engine/statistics: >= 90%
- core/plugin_system: >= 80%
- core/ai: >= 70%
- backend/service: >= 80%
- 项目整体: >= 80%

## 6. 架构测试

验证层隔离约束不被违反:

```python
def test_engine_does_not_import_sqlalchemy():
    violations = check_imports(
        "engine/",
        forbidden=["sqlalchemy", "httpx", "aiofiles"]
    )
    assert len(violations) == 0

def test_service_does_not_import_ui_libs():
    violations = check_imports(
        "backend/service/",
        forbidden=["fastapi", "click", "rich"]
    )
    assert len(violations) == 0
```
