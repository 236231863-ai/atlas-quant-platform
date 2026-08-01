# Atlas Quant Platform — Git Workflow

> Sprint E1 · Phase 1 交付物

## 1. 分支策略（Branch Strategy）

```
main          ← 生产环境，仅可发布 tag
  └── release/    ← 发布候选分支（RC）
       └── develop  ← 集成开发分支（默认开发目标）
            ├── feature/*  功能分支（从 develop 切出，合并回 develop）
            └── hotfix/*   热修复分支（从 main 切出，合并回 main + develop）
```

| 分支 | 用途 | 来源 | 合并目标 |
|------|------|------|---------|
| `main` | 生产 / 正式发布 | — | tag |
| `develop` | 日常集成 | main | main（发版时） |
| `release/*` | 发布候选（RC） | develop | main |
| `feature/*` | 新功能 | develop | develop |
| `hotfix/*` | 紧急修复 | main | main + develop |

## 2. Commit Convention（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

footer
```

**Type**：`feat`（功能）/ `fix`（修复）/ `refactor`（重构）/ `docs`（文档）/ `test`（测试）/ `chore`（杂务）/ `build`（构建）/ `ci`（CI）/ `style`（格式）

**示例**：
```
feat(desktop): implement dashboard metric cards
fix(backend): resolve 502 on proxy upstream
build: unify packaging pipeline with build.ps1
```

## 3. Tag Convention

```
v<major>.<minor>.<patch>[-rc<N>]
```

示例：
- `v3.5.2` — 正式版
- `v3.6.0-rc1` — 发布候选 1
- `v4.0.0` — 商业版

每个 Release tag 必须附注（annotated）：`git tag -a v3.5.2 -m "..."`

## 4. Version Strategy（SemVer）

```
major.minor.patch
```

| 变化 | 版本位 | 示例 |
|------|--------|------|
| 破坏性 API 变更 / 商业大版本 | major | 3.x → 4.0.0 |
| 向后兼容的新功能 | minor | 3.5 → 3.6.0 |
| Bug 修复 | patch | 3.5.2 → 3.5.3 |
| 发布候选 | 追加 `-rcN` | 3.6.0-rc1 |

版本号统一维护在 `pyproject.toml`，发版时同步 README 与 CHANGELOG。
