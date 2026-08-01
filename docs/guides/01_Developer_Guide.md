# Developer Guide

## 环境要求

- Python 3.11+
- Git
- VSCode（推荐）

## 工程结构

```
AtlasQuant/
  core/       - 领域核心类型
  engine/     - 量化研究引擎
  backend/    - FastAPI 服务
  apps/       - 应用层
  desktop/    - PySide6 桌面端
  plugins/    - 彩种插件
  tests/      - 测试
  packaging/  - PyInstaller spec
  engineering/ - 工程规范
```

## 开发流程

1. 从 `develop` 分支切功能分支：`git checkout develop && git checkout -b feature/xxx`
2. 开发（遵循 ENGINEERING_RULES.md）
3. `ruff check .` + `pytest` 通过
4. 提交（Conventional Commits）+ 推送到 origin
5. 提 PR 到 develop

## 调试

- 桌面：VSCode F5 → "Desktop (Atlas GUI)"
- 后端：F5 → "Backend (FastAPI)"
- 测试：F5 → "Pytest (Current File)"

## 构建

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -Target all
```

## 打包

```powershell
powershell -ExecutionPolicy Bypass -File packaging/package.ps1 -All
```
