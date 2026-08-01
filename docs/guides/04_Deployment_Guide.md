# Deployment Guide

## Docker 部署

```bash
# 构建并启动全部服务（backend/frontend/nginx/postgres/redis）
docker compose -f docker/docker-compose.yml up -d

# 查看状态
docker compose -f docker/docker-compose.yml ps

# 停止
docker compose -f docker/docker-compose.yml down
```

### 服务端口

| 服务 | 端口 |
|------|------|
| nginx（Web 入口） | 80 |
| backend（FastAPI） | 8000 |
| postgres | 5432 |
| redis | 6379 |

## 开发环境覆盖

```bash
# 自动加载 compose.override.yml（热挂载 + 调试 + reload）
docker compose up -d
```

## 桌面端部署

- 安装程序：运行 `Atlas_Setup.exe`
- 便携版：解压 `Atlas_Portable.zip`
- 桌面版内置数据，不依赖后端服务

## 环境变量

参考 `.env.example`：

```
ATLAS_ENVIRONMENT=production
ATLAS_DB__URL=postgresql+asyncpg://atlas:atlas_secret@localhost:5432/atlas
ATLAS_LOG__LEVEL=INFO
```
