# Atlas Quant Platform - Codex 工作规则

> 每次启动新任务前阅读此文件。

## 核心约束

1. **层隔离** - UI不能直接访问Data, Engine不能碰DB
2. **引擎纯计算** - Engine层不导入 sqlalchemy/httpx/aiofiles
3. **策略是JSON** - 策略定义是数据不是代码
4. **插件化** - 新增彩种=新增插件, 不修改主程序
5. **AI不碰DB** - AI服务只能调用Engine获取数据

## 工作流程

1. 先阅读对应Prompt Library中的模板
2. 一次只做一件事 (建表/写引擎/写测试 分开)
3. 先写测试再实现
4. 保持函数签名类型注解完整

## 文档参考

管理体系文档位于 docs/management/:
- 00: 项目章程
- 01: 产品需求
- 02: 系统架构
- 03: 开发规范
- 04: Prompt Library (10个模板)
- 05: Sprint管理
- 06: 测试规范
- 07: 发布规范
- 08: 文档模板
