# Atlas Quant Platform — Dependency Report

> Sprint E1 · Phase 3 交付物
> 生成时间：2026-08-02

## 1. 依赖分层结构

```
requirements.txt              核心（跨模块）
 ├── requirements-desktop.txt  桌面（PySide6/matplotlib）
 ├── requirements-web.txt      Web（uvicorn）
 ├── requirements-ai.txt       AI 适配层
 ├── requirements-enterprise.txt  企业版
 └── requirements-dev.txt      开发（pytest/ruff/black/mypy）
constraints.txt               版本锁定（上限约束）
```

## 2. 当前环境实测版本（2026-08-02）

| 包 | 版本 | 归属 | 状态 |
|----|------|------|------|
| fastapi | 0.138.1 | core | ✅ |
| pydantic | 2.13.4 | core | ✅ |
| pydantic-settings | 2.14.2 | core | ✅ |
| sqlalchemy | 2.0.51 | core | ✅ |
| pandas | 3.0.3 | core | ✅ |
| numpy | 2.5.0 | core | ✅ |
| PySide6 | 6.11.1 | desktop | ✅ |
| matplotlib | 3.11.1 | desktop | ✅ |
| uvicorn | 0.29.0 | web | ✅ |
| pytest | 9.1.1 | dev | ✅ |
| httpx | 0.28.1 | ai/cli | ✅ |
| alembic | — | core | 待装 |
| scipy | — | engine | 待装 |
| scikit-learn | — | engine | 待装 |
| ruff | — | dev | 待装 |

## 3. 版本约束策略

- **requirements\*.txt**：声明下限 `>=`，保证可用最小版本
- **constraints.txt**：声明上限 `<`，防止意外大版本升级破坏 API
- 组合效果：`>=x.y, <x.y+1` 的受控范围，兼顾兼容与可复现

## 4. 可复现性

```bash
pip install -r requirements-dev.txt -c constraints.txt
```

即可在同一约束下复现开发环境。
