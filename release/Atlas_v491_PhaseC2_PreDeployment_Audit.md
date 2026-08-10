# Atlas v4.9.1 — Phase C.2 部署前审计（Pre-Deployment Audit）

> 阶段：Phase C.2 · 性质：审计（禁止新增功能/修改产品逻辑）
> 目的：确认腾讯云部署前所有条件满足
> 状态：✅ 审计完成 · 1 项需执行（CORS）+ 2 项决策

---

## P0 环境

| # | 项 | 状态 | 详情 |
|---|----|:---:|------|
| 1 | **FastAPI 启动入口** | ✅ | `backend/mobile/api.py` 定义 router（含 auth_router/mobile router）；app 由启动命令 `uvicorn.run(app)` 组装（含 include_router）。无独立 app.py，迁移时需在服务器端提供启动脚本 |
| 2 | **requirements.txt** | ✅ | fastapi/uvicorn/pydantic/sqlalchemy 均 >= 指定版本 |
| 3 | **Python 版本兼容** | ✅ | pyproject 要求 `^3.11`；当前 3.14 运行正常；服务器装 3.11+ 即可 |
| 4 | **SQLite 数据库路径** | ✅ | `~/.atlas/mobile_mvp.db`，`ATLAS_STORAGE_DIR` 可覆盖 → 服务器设 `/opt/atlas/data` |
| 5 | **环境变量清单** | ✅ | `WECHAT_APPID` / `WECHAT_APPSECRET` / `WECHAT_LOGIN_MOCK` / `WECHAT_MOCK` / `WECHAT_TEMPLATE_ID` / `ATLAS_STORAGE_DIR` |
| 6 | **微信登录配置** | ✅ | `WeChatLoginClient` 读环境变量；无密钥时 mock 兜底（`WECHAT_LOGIN_MOCK=1`） |

## P1 网络

| # | 项 | 状态 | 详情 |
|---|----|:---:|------|
| 1 | **API_BASE 切换位置** | ✅ 单点 | `mobile_app/utils/api.js` 第 5 行 `BASE`；`AUTH_BASE` 由 BASE replace 推导 → **改 BASE 一处，auth 自动跟随** |
| 2 | **HTTPS 需求** | ⚠️ 需配 | 小程序正式/体验版要求 HTTPS；腾讯云免费 DV 证书 + Nginx |
| 3 | **微信 request 合法域名** | ⚠️ 需配 | 小程序后台添加 `https://api.atlas-lottery.com` |
| 4 | **CORS 配置** | ⚠️ **未配置** | `api.py` 无 CORSMiddleware。小程序 wx.request 原生请求不受 CORS 限制（不阻塞 Beta），但浏览器/Web 调试需要。**建议部署时在启动脚本加 CORSMiddleware**（属部署配置，非业务逻辑） |

## P2 数据

| # | 项 | 状态 | 详情 |
|---|----|:---:|------|
| 1 | **SQLite 迁移方式** | ✅ | 文件直接上传（scp/rsync），结构零改动 |
| 2 | **初始数据是否为空** | ⚠️ **非空** | 当前库：users=2、tickets=2、draws=1702、events=11。其中 **2 用户为 demo_openid 测试数据**（真机验证产生） |
| 3 | **备份恢复流程** | ✅ | 每日 cron 备份（保留 14 天）+ 恢复 = 复制回 data 目录 |

### ⚠️ 数据决策点（Beta 前必选）
- **方案 A（推荐）**：云端**清空** users/tickets/reminders/events（保留 draws 开奖数据），Beta 从真实微信登录重新建档 → 数据干净可信
- 方案 B：原样迁移（保留 2 个 demo 用户）→ 污染留存统计，不推荐

## P3 安全

| # | 项 | 状态 | 详情 |
|---|----|:---:|------|
| 1 | **AppSecret 存储** | ✅ | 仅环境变量，代码零硬编码（grep 实证） |
| 2 | **日志脱敏** | ✅ | 登录/事件不记录 openid/session_key/secret |
| 3 | **用户隔离验证** | ✅ | openid 唯一约束 + ticket 按 user_id 过滤（已有测试覆盖） |

---

## 审计结论

| 项 | 结论 |
|----|------|
| **阻塞项** | 无硬阻塞。部署前需：① 启动脚本加 CORSMiddleware（可选但建议）② HTTPS+域名 ③ request 合法域名 |
| **需决策** | ① 数据是否清空重建（推荐 A）② 服务器地域（香港免备案/大陆需备案） |
| **可部署** | ✅ 代码零改动，满足上云条件 |

---

## 部署前 To-Do（按审计结论）

- [ ] 服务器端提供 `start_server.py`（FastAPI app + include_router + CORSMiddleware）
- [ ] 云端清空 demo 数据（保留 draws）→ Beta 真实登录重建
- [ ] 配置 HTTPS + request 合法域名
- [ ] 环境变量（含真实 WECHAT_APPSECRET）
- [ ] 每日备份 cron

---

## 红线确认

- ✅ 未新增功能 / 未修改产品逻辑
- ✅ 仅审计与部署配置建议
