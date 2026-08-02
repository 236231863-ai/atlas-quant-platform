# Phase 6 — Web 版本规划报告

> Atlas Quant Platform v3.6.0 Product Launch
> 日期：2026-08-02

---

## 一、现状评估（Web 化基础）

### 后端 API（FastAPI，13 路由就绪）

| 领域 | 路由 |
|------|------|
| 数据看板 | `/dashboard/summary` |
| 开奖数据 | `/{lottery}/draws`、`/{lottery}/latest`、`/{lottery}/statistics` |
| 策略 | `/strategies/ranking` |
| 实验 | `/experiments/history` |
| 研究 | `/research/reports` |
| 用户 | `/users`、`/users/{uid}`、`/users/{uid}/workspaces`、`/workspaces` |
| 系统 | `/health` |

### 前端（Vite + TypeScript 就绪）
- `frontend/`：Vite + TS 工程，`index.html` + `src/`
- 可打包为静态站，由 nginx 服务

### 部署（Docker 就绪）
- 5 服务编排：backend/frontend/nginx/postgres/redis（E1 Phase 7）
- `docker compose up` 即可运行

## 二、Web 产品形态

| 维度 | 桌面版 v3.6.0 | Web 版（规划） |
|------|--------------|---------------|
| 定位 | 本地量化研究工作站 | 多端访问的数据分析平台 |
| 数据 | 本地 CSV（用户导入） | 后端数据库（多用户共享） |
| AI | 本地/在线（个人 Key） | 服务端统一配置 |
| 账户 | 本地档案 | 云端账户（多用户） |
| 场景 | 单机深度分析 | 团队/移动端查看 |

## 三、Web 版本路线图（建议）

| 阶段 | 内容 | 前置 |
|------|------|------|
| W1 MVP | 数据看板 + 开奖查询 Web 化 | 后端数据接入 |
| W2 | 统计图表 + 报告在线化 | 图表组件 |
| W3 | 用户系统 + 数据看板权限 | 账户服务 |
| W4 | 策略/回测在线化 | 计算服务 |

## 四、部署方案

```bash
# 生产：docker compose 5 服务
docker compose -f docker/docker-compose.yml up -d
# 访问 http://localhost （nginx → frontend + backend /api）
```

## 五、与桌面版差异矩阵

| 能力 | 桌面 | Web |
|------|------|-----|
| 安装 | 需安装（Setup.exe） | 免安装，浏览器访问 |
| 离线 | ✅ 完全离线 | ❌ 需联网 |
| 性能 | 本地计算 | 服务端计算 |
| 数据量 | 本地 CSV | 数据库可大容量 |
| 多用户 | ❌ | ✅ |
| 移动端 | ❌ | ✅ |

## 六、4 问回答（Web 规划）

### 1. 用户在哪里下载？
Web 版无需下载，浏览器访问部署地址。

### 2. 用户如何安装？
无需安装；运维执行 `docker compose up` 部署。

### 3. 用户如何第一次使用？
浏览器打开 → 登录 → 查看数据看板。

### 4. 用户获得什么价值？
多端访问、团队协作、集中数据管理。

## 七、结论

Web 版基础完备（API + 前端 + Docker 全就绪），建议作为 **v3.7.0 主要方向** 推进 W1 MVP。本次 v3.6.0 以桌面版为主打。
