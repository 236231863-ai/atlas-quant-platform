# 001: 新建引擎模块

> 用途: 在engine/下创建纯计算模块
> 前置: 引擎接口设计已完成
> 输出: engine/<module>/ 下的Python代码 + 单元测试

## Prompt模板

"""
请阅读以下文档了解本项目规范:

1. docs/management/03_Development_Standards/README.md
2. docs/management/02_System_Architecture/README.md
3. engine/__init__.py (了解已有引擎结构)

现需要在 engine/<module_name>/ 下创建 <module_description> 模块。

## 需求

<具体功能描述>

## 接口

输入: <输入数据结构>
输出: <输出数据结构>

## 约束

1. 纯计算函数，无副作用
2. 不导入 sqlalchemy / httpx / aiofiles 等框架
3. 不读写文件
4. 不访问数据库
5. 所有随机种子由参数控制
6. 函数签名包含完整类型注解
7. 每个函数有 Google 风格的 docstring
8. 边缘情况有处理 (空数据、单条数据、异常值)

## 测试

为每个函数创建对应的单元测试:
- 正常输入测试
- 边界条件测试 (空列表、单元素等)
- 异常输入测试
- 稳定性测试 (相同输入 = 相同输出)
"""
