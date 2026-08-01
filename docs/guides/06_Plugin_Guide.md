# Plugin Guide

## 插件体系

Atlas 使用插件化设计，每种彩票（彩种）是一个插件。

现有插件：

| 插件 | 说明 |
|------|------|
| `plugins/dlt` | 大乐透 |
| `plugins/ssq` | 双色球 |

## 插件结构

```
plugins/<code>/
  plugin.json    # 插件元数据（彩种定义）
  engine.py      # 玩法计算
  ...
```

## plugin.json 示例

```json
{
  "code": "dlt",
  "name": "大乐透",
  "main_range": { "min": 1, "max": 35, "count": 5 },
  "bonus_range": { "min": 1, "max": 12, "count": 2 }
}
```

## 注册新插件

1. 在 `plugins/` 下新建目录
2. 编写 `plugin.json` 定义彩种规则
3. 在 `engine/plugins/registry.py` 注册
4. 添加测试

## 入口

插件必须通过 CLI、Desktop、API 或 SDK 之一可访问。
