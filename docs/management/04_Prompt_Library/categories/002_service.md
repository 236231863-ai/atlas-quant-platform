# 002: 新建Service

> 用途: 在backend/service/下创建编排层
> 前置: Engine模块已完成
> 输出: backend/service/<name>.py + 集成测试

## Prompt模板

"""
请阅读以下文档:

1. docs/management/03_Development_Standards/README.md
2. docs/management/02_System_Architecture/README.md
3. backend/service/ (了解已有Service结构)

现需要创建 <service_name> Service。

## 需求

<具体服务功能>

## 编排逻辑

1. 接收 <输入>
2. 从 Data Layer 获取 <数据>
3. 调用 Engine 的 <模块> 进行计算
4. 将结果保存到 Data Layer
5. 返回 <输出>

## 约束

1. Service层不包含计算逻辑 (调用Engine)
2. Service层编排业务流程
3. 管理事务边界
4. 将基础设施异常转换为领域异常
5. 记录审计日志

## 集成测试

- 使用内存数据库
- Mock Engine层
- 测试完整编排路径
- 测试错误路径
"""
