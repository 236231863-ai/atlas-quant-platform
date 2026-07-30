# 004: 新建插件

> 用途: 在plugins/下创建新彩种插件
> 前置: Plugin系统接口已定义
> 输出: plugins/<name>/ 下的完整插件

## Prompt模板

"""
请阅读以下文档:

1. docs/management/02_System_Architecture/README.md (插件章节)
2. core/plugin_system/ (插件系统接口)
3. plugins/<参考插件>/ (参考已有插件)

现需要创建 <plugin_name> 插件。

## 彩种信息

- 名称: <彩种名称>
- 主号码范围: <范围>
- 特别号码范围: <范围> (如无则忽略)
- 开奖频率: <每周几次>
- 数据源URL: <URL>

## 插件内容

1. plugin.json: 插件元数据
2. plugin.py: 实现PluginABC接口
3. data_source.py: 数据采集适配器 (如有HTTP源)
4. strategies.json: 预置策略模板 (可选)

## 约束

1. 插件不包含业务逻辑 (调用Service)
2. 插件不包含计算逻辑 (调用Engine)
3. 插件只包含领域定义和数据源适配
"""
