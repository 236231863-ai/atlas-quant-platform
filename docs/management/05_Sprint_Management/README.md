# Atlas Quant Platform - Sprint 管理规范

> 版本: 1.0
> 创建日期: 2026-07-28

---

## 1. Sprint 周期

- 标准周期: 2周
- 复杂Sprint: 3周
- 每个Sprint以回顾会议结束

## 2. Sprint 流程

Day 1:   Sprint Planning (需求细化 + 任务分配)
Day 2-9: 开发阶段
Day 10:  Code Freeze + 测试 + Review
Day 11:  Sprint Review (演示 + 回顾)
Day 12:  下一个Sprint Planning / 缓冲期

## 3. Sprint 工件

### Sprint Backlog

从产品Backlog中选择当前Sprint要完成的任务。
每个任务需要:
- 清晰的验收标准
- 预估工时
- 负责人
- 依赖关系

### Sprint Board

使用看板追踪状态:
- Backlog: 待处理
- In Progress: 开发中
- Review: 代码审查中
- Testing: 测试中
- Done: 已完成

## 4. Sprint 节奏

### 每日站会 (15分钟)

- 昨天做了什么?
- 今天计划做什么?
- 有什么阻塞?

### Code Review

- 每个PR必须review
- Review标准: 正确性 + 架构合规 + 测试覆盖
- 24小时内响应

### Sprint Review

- 演示已完成功能
- 收集反馈
- 更新产品Backlog

### Sprint Retrospective

- 哪些做得好?
- 哪些可以改进?
- 下次Sprint的改进措施

## 5. Sprint 0 (当前)

已完成: 项目架构设计、管理文档、项目骨架

## 6. Sprint 计划

### Sprint 1: 数据层 (2周)
目标: 完成数据采集、存储、查询基础设施

### Sprint 2: 引擎核心 (3周)
目标: 完成分析引擎、统计引擎

### Sprint 3: 回测引擎 (2周)
目标: 完成回测引擎、策略基础框架

### Sprint 4: 策略系统 (2周)
目标: 策略实验室、参数优化

### Sprint 5: 界面 (3周)
目标: CLI完善、Web Dashboard MVP、AI集成

### Sprint 6: 工程化 (2周)
目标: 性能优化、测试完善、文档、容器化
