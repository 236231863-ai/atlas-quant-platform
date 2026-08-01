# Contributing to Atlas Quant Platform

感谢你愿意为 Atlas Quant Platform 贡献代码。请先阅读并遵守以下准则。

## 开发流程

1. 从 `develop` 分支切出功能分支：`git checkout develop && git checkout -b feature/your-feature`
2. 遵循 [Git Workflow](engineering/Git_Workflow.md) 的分支与提交规范
3. 提交信息遵循 Conventional Commits：`feat:` / `fix:` / `refactor:` / `docs:` / `test:` / `chore:` / `build:`
4. 开发完成后运行完整测试并确保通过
5. 提交 Pull Request 到 `develop` 分支

## 代码规范

- Python 遵循 PEP8 + Ruff 检查：`poetry run ruff check .`
- 类型标注（Type Hint）与 Docstring 为必需
- 新增模块必须提供入口（Desktop/Web/CLI/REST API/SDK/Plugin）
- 用户功能必须 Backend → API → Frontend → Docs → Tests 完整交付

## 工程规则

遵守 `ENGINEERING_RULES.md` 中 18 条强制规则，重点：

- **禁止重复开发**：先扫描既有模块，复用优先
- **禁止只有 Backend**：用户功能必须全链路
- **保持 Release 可构建**：任何改动不得破坏 Build/Installer/Release
- **成果必须真实可验证**：禁止"理论完成"

## 测试要求

- 每个 Phase 结束必须运行：Unit / Integration / Regression / Smoke Test
- 新增功能必须有对应测试

## 提交前检查清单

- [ ] `poetry run ruff check .` 通过
- [ ] `poetry run pytest` 通过
- [ ] README / 文档已同步更新
- [ ] 构建验证通过（桌面/后端/Web 任一受影响模块）
