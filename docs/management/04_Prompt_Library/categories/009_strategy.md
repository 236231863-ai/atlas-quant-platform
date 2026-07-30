# 009: 新建策略 (JSON)

> 用途: 创建JSON策略定义和处理器
> 前置: 策略引擎已完成
> 输出: 策略JSON文件 + 策略处理器 (可选)

## Prompt模板

"""
请阅读以下文档:
1. engine/strategy/ (策略引擎接口)
2. docs/management/02_System_Architecture/README.md (策略章节)

## 策略需求

- 名称: <策略名称>
- 类型: filter | weighted | combination
- 描述: <策略描述>

## 策略逻辑

<描述策略的计算逻辑>

## 约束

1. 策略定义为JSON
2. 所有参数可配置
3. 包含版本号
4. 包含元数据 (作者、描述)
5. 如需自定义计算逻辑，放在 engine/strategy/builtin/

## 输出

1. strategies/<name>.json (策略定义)
2. engine/strategy/builtin/<name>.py (如需自定义处理器)
3. tests/unit/strategy/test_<name>.py (单元测试)
"""
