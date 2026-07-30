# 006: 写集成测试

> 用途: 为Service/Data层写集成测试
> 前置: Service/Data层代码已完成
> 输出: tests/integration/ 下的测试文件

## Prompt模板

"""
请阅读以下文档:

1. docs/management/06_Test_Specifications/README.md
2. <要测试的模块代码>

现需要为 <module> 模块编写集成测试。

## 要求

1. 测试Service层的编排逻辑
2. 测试Data层的数据库交互
3. 使用内存SQLite数据库
4. 使用 pytest.mark.integration 标记
5. 每个测试独立 (setup/teardown)

## 测试内容

- Repository CRUD操作
- Use Case完整编排
- 数据库迁移验证
- 事务回滚测试

## 示例

```python
@pytest.mark.integration
class TestDrawRepository:
    async def test_save_and_find(self, db_session):
        ...

    async def test_find_by_date_range(self, db_session):
        ...
```
"""
