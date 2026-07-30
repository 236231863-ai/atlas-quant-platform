# Atlas Quant Platform - Codex Prompt Library

> 版本: 1.0
> 创建日期: 2026-07-28

---

## 设计原则

Codex 的每次对话应该只做一件事。

不要:
- 在一个prompt里同时: "建表、写API、画页面"

应该:
- 001: 建表 - 只做数据库Schema
- 002: 写引擎 - 只做计算逻辑
- 003: 写测试 - 只做测试

这样做的原因:
- 代码质量大幅提高 (每步可review)
- 错误容易定位 (回退成本低)
- Codex上下文不溢出 (输出更精确)
- 代码审查更高效 (每次只审查一件事)

## Prompt分类

按工作类型分为:

| 编号 | 类型 | 用途 |
|------|------|------|
| 001 | 新建引擎模块 | 在engine/下创建纯计算模块 |
| 002 | 新建Service | 在backend/service/下创建编排层 |
| 003 | 新建API端点 | 在backend/api/下创建REST端点 |
| 004 | 新建插件 | 在plugins/下创建新彩种插件 |
| 005 | 写单元测试 | 为Engine模块写单元测试 |
| 006 | 写集成测试 | 为Service/Data层写集成测试 |
| 007 | 修复Bug | 定位并修复特定bug |
| 008 | 重构 | 不改变行为的重构 |
| 009 | 新建策略 | 创建JSON策略定义和处理器 |
| 010 | 数据迁移 | 数据库Schema变更 |

## 使用方式

1. 打开Codex新对话
2. 复制对应的prompt模板
3. 填充具体参数
4. 发送给Codex

## 重要原则

每次对话前，先引用管理体系文档:
- "阅读 docs/management/03_Development_Standards 了解编码规范"
- "阅读 plugins/ssq/ 了解插件结构"
- "阅读 engine/backtest/README.md 了解接口约定"

这样Codex不会发明自己的规范。
