# 003: 新建API端点

> 用途: 在backend/api/v1/下创建REST端点
> 前置: Service模块已完成
> 输出: backend/api/v1/<name>.py + 请求/响应Schema

## Prompt模板

"""
请阅读以下文档:

1. docs/management/02_System_Architecture/README.md
2. backend/api/v1/ (了解已有API结构)

现需要创建 <endpoint> API 端点。

## 需求

- 方法: GET|POST|PUT|DELETE
- 路径: /api/v1/<path>
- 功能: <描述>

## 请求

<请求参数>

## 响应

<响应格式>

## 约束

1. API不包含业务逻辑, 直接调用Service
2. 输入通过Pydantic模型校验
3. 响应统一格式
4. 异常统一处理
5. 所有响应附带 X-LQRP-Disclaimer 头
"""
