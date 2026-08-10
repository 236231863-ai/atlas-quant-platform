# Atlas v4.9.1 — Phase C.1 云端迁移计划（Cloud Migration Plan）

> 阶段：Phase C.1 · 状态：✅ 方案就绪 · 待执行
> 目标：将局域网运行版本迁移到公网 Beta 环境，解除局域网限制
> 原则：P0 冻结，禁止新增产品功能；只改 API_BASE_URL + 部署配置

---

## 1. 环境检查（现状）

| 项 | 现状 |
|----|------|
| **FastAPI 启动** | `uvicorn.run(app, host='0.0.0.0', port=8000)`，入口在启动命令（`backend/mobile/api.py` 定义 router） |
| **SQLite 路径** | `~/.atlas/mobile_mvp.db`（`ATLAS_STORAGE_DIR` 可覆盖） |
| **配置文件** | `backend/mobile/db.py`（DB 路径）· `mobile_app/utils/api.js`（API BASE）· `project.config.json`（appid） |
| **API 地址引用** | `api.js` BASE = `http://192.168.31.95:8000/api/mobile/v1`（局域网） |
| **依赖** | `requirements.txt`（fastapi/uvicorn/pydantic/sqlalchemy） |
| **Python 版本** | pyproject 要求 `^3.11`（当前 3.14 可跑） |
| **当前端口** | 8000 监听中（0.0.0.0） |

---

## 2. 腾讯云部署方案

### 服务器配置（推荐）

| 项 | 配置 | 说明 |
|----|------|------|
| 机型 | 腾讯云**轻量应用服务器** 2C2G | Beta 阶段足够 |
| 系统 | **Ubuntu 22.04 LTS** | 稳定 + 文档多 |
| 地域 | **香港**（免 ICP 备案，Beta 快速上线）或 大陆（需备案） | 见风险 |
| Python | **3.11**（系统或 pyenv） | 匹配 pyproject |
| 带宽 | 4-5 Mbps | 10 人并发足够 |
| 价格 | ~¥50-70/月 | |

### Linux 环境安装步骤

```bash
# Ubuntu 22.04
sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx

# 项目代码
sudo mkdir -p /opt/atlas && cd /opt/atlas
# 上传 backend/mobile + engine + requirements.txt

# 虚拟环境 + 依赖
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 环境变量（不写入代码）
export WECHAT_APPID=wxe254d2aded63ca94
export WECHAT_APPSECRET=<你的AppSecret>
export WECHAT_LOGIN_MOCK=0
export ATLAS_STORAGE_DIR=/opt/atlas/data
```

### 防火墙

```bash
# 仅开放 80/443，8000 不对外
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp     # SSH（建议仅白名单 IP）
sudo ufw enable
```

> ⚠️ uvicorn 监听 127.0.0.1:8000（不暴露公网），由 Nginx 反向代理。

### HTTPS 方案

```nginx
# /etc/nginx/sites-available/atlas
server {
    listen 443 ssl;
    server_name api.atlas-lottery.com;

    ssl_certificate     /etc/ssl/certs/fullchain.pem;   # 腾讯云免费 DV 证书
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
server {
    listen 80;
    server_name api.atlas-lottery.com;
    return 301 https://$host$request_uri;
}
```

- 证书：腾讯云 SSL 免费 DV 证书（1 年）
- 小程序后台：`request 合法域名` 添加 `https://api.atlas-lottery.com`

---

## 3. 迁移设计（保持一切不变，只改两处）

### 保持不变

| 项 | 保证 |
|----|------|
| 数据结构 | `mobile_mvp.db` 5 表原样迁移 |
| 埋点体系 | 17 事件 + 冻结指标不变 |
| 用户体系 | openid ↔ U_ID 不变 |
| 小程序页面 | 8 页面结构不变 |

### 只修改两处

| 文件 | 修改 |
|------|------|
| `mobile_app/utils/api.js` | BASE → `https://api.atlas-lottery.com/api/mobile/v1` |
| 部署配置 | 环境变量 + Nginx + 防火墙（见上） |

> ✅ **业务代码零改动**：`backend/mobile/` 与 `mobile_app/pages/` 全部不动。

---

## 4. 数据安全

### SQLite 每日备份

```bash
# cron 每日 3:00
0 3 * * * cp /opt/atlas/data/mobile_mvp.db /opt/atlas/backups/mobile_mvp_$(date +\%F).db
0 3 * * * find /opt/atlas/backups -mtime +14 -delete   # 保留 14 天
```

### 日志脱敏
- ✅ 后端不记录 openid/session_key/AppSecret
- ✅ 行为事件只存事件名+U_ID（无身份隐私）
- ✅ Nginx 访问日志可保留 IP，不关联用户身份

### 用户隔离验证（迁移后必测）
| 用例 | 预期 |
|------|------|
| 用户 A 登录 → 返回原 U_ID | ✅ |
| 用户 A 看不到用户 B 的票 | ✅（ticket 按 user_id 过滤） |
| 未授权访问他人 user_id | 返回空/404 |

---

## 5. 迁移执行清单（产品负责人）

| 步骤 | 动作 | 耗时 |
|------|------|------|
| 1 | 购买腾讯云轻量服务器 + 域名 | 1 天 |
| 2 | 域名解析（A 记录 → 服务器 IP） | 10 分钟 |
| 3 | Linux 环境 + Python 3.11 + 依赖 | 2 小时 |
| 4 | 上传代码 + 配置环境变量 | 1 小时 |
| 5 | Nginx + HTTPS 证书 | 2 小时 |
| 6 | 小程序后台配置 request 合法域名 | 10 分钟 |
| 7 | 更新 api.js BASE → https | 5 分钟 |
| 8 | 重新上传体验版 + 真机异地验证 | 1 小时 |
| 9 | 数据备份 cron + 隔离验证 | 30 分钟 |

**合计约 2-3 天**（含服务器购买与域名解析等待）。

---

## 风险与备注

| 项 | 说明 |
|----|------|
| ICP 备案 | 大陆节点需备案（7-20 天）；**建议选香港节点**免备案快速上线 |
| 域名 | 需在腾讯云控制台做实名认证 |
| 数据迁移 | SQLite 文件直接上传（scp/rsync），结构零改动 |
| 回滚 | 保留局域网版 api.js（git 分支），随时可切回 |

---

## 结论

> Phase C.1 迁移**零业务代码改动**，只改 API_BASE_URL + 部署配置。腾讯云香港轻量服务器约 ¥60/月，2-3 天可完成。部署完成后用户可**异地**使用小程序。
