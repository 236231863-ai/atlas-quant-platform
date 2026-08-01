# Architecture Guide

## 核心哲学

```
UI → API → Service → Engine → Data → DB
                      ↑
                所有计算在这里
```

## 分层

| 层 | 目录 | 职责 |
|----|------|------|
| 展现层 | `desktop/`、`apps/`、`frontend/` | UI（桌面/Web） |
| API 层 | `backend/api/` | FastAPI 路由 |
| 服务层 | `backend/service/` | 业务编排 |
| 引擎层 | `engine/` | 所有数学/统计计算 |
| 领域层 | `core/` | 类型、异常、插件系统 |
| 数据层 | `backend/database/` | ORM、仓储 |
| 插件层 | `plugins/` | 彩种插件 |

## 依赖方向

```
Desktop/Web → Backend/API → Service → Engine → Core
                                        ↓
                                     Plugins
```

高层依赖低层，禁止反向依赖。`engine` 为计算核心，被多端复用。

## 桌面端架构

```
desktop/
  main.py          # 入口
  windows/         # 主窗口 + 导航
  pages/           # 6 个功能页面
  charts/          # matplotlib 图表
  data_loader.py   # 内置数据层（CSV）
  stats.py         # 统计计算
  api_client.py    # 可选后端客户端
```

## 完整架构图

见 `engineering/Sprint_E1_Architecture.md`。
