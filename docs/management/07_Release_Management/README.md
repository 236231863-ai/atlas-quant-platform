# Atlas Quant Platform - 发布规范

> 版本: 1.0
> 创建日期: 2026-07-28

---

## 1. 版本号规范

遵循 Semantic Versioning 2.0:

vMAJOR.MINOR.PATCH

- MAJOR: 不兼容的API变更
- MINOR: 向后兼容的功能新增
- PATCH: 向后兼容的bug修复

## 2. 版本阶段

- v0.1.x - v0.7.x: 开发阶段, 内部发布
- v1.0.0-rc.x: 候选发布版
- v1.0.0: 正式版

## 3. 发布流程

```
develop 分支
    |
    代码冻结 (Code Freeze)
    |
    创建 release/vX.Y.Z 分支
    |
    最终测试 + Bug修复
    |
    合并到 main
    |
    打标签 vX.Y.Z
    |
    CI/CD 自动构建:
    |   - PyPI 发布
    |   - Docker 镜像构建
    |   - 文档发布
    |
    创建 GitHub Release
    |
    合并回 develop
```

## 4. 发布检查清单

### 代码检查
- [ ] 所有测试通过
- [ ] 覆盖率达标
- [ ] mypy strict mode通过
- [ ] Ruff lint零警告
- [ ] 架构测试通过
- [ ] 安全审计通过

### 文档检查
- [ ] CHANGELOG 已更新
- [ ] API文档已更新
- [ ] 升级指南已编写 (如需)
- [ ] README已更新

### 构建检查
- [ ] Poetry build 成功
- [ ] Docker build 成功
- [ ] 安装测试通过

## 5. CHANGELOG 格式

```markdown
# Changelog

## [v0.2.0] - 2026-08-11

### Added
- feat(collector): 双色球数据采集适配器
- feat(analysis): 频率分析引擎

### Changed
- refactor(engine): 重构分析引擎接口

### Fixed
- fix(backtest): 修正最大回撤计算

### Security
- security: 升级依赖版本
```

## 6. 发布候选版 (Release Candidate)

- 格式: v1.0.0-rc.1, v1.0.0-rc.2
- RC阶段至少测试1周
- RC阶段的bug fix直接提交到release分支
- 无新增功能

## 7. 热修复 (Hotfix)

- 从main创建 hotfix/X.Y.Z 分支
- 修复后同时合并到main和develop
- 版本号增加PATCH
- 紧急情况下可跳过部分流程，但必须经过测试

## 8. 版本维护策略

- 每个大版本维护12个月
- 下个版本发布前6个月宣布弃用计划
- LTS版本维护24个月
