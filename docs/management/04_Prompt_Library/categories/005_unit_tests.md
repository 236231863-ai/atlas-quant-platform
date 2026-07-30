# 005: 写单元测试

> 用途: 为Engine模块写单元测试
> 前置: Engine模块代码已完成
> 输出: tests/unit/engine/<module>/ 下的测试文件

## Prompt模板

"""
请阅读以下文档:

1. docs/management/06_Test_Specifications/README.md
2. <要测试的模块代码>

现需要为 engine/<module> 模块编写单元测试。

## 要求

1. 每个公共函数对应一个测试文件
2. 每个函数至少覆盖:
   - 正常路径 (happy path)
   - 边界条件 (空数据、单条、最大值)
   - 异常输入 (无效参数)
3. 不Mock引擎内部函数 (只Mock外部依赖)
4. 测试名称格式: test_<函数名>_<场景>
5. 使用 pytest.mark.unit 标记

## 示例

```python
import pytest
import pandas as pd
from engine.analysis.calculators.frequency import calculate_frequency

class TestCalculateFrequency:
    def test_normal_case(self):
        ...

    def test_empty_data(self):
        ...

    def test_single_element(self):
        ...

    def test_invalid_input_raises(self):
        ...
```
"""
