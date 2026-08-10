# Atlas v4.9.1 — Phase C.3 云端部署准备报告（Cloud Deployment Preparation）

> 阶段：Phase C.3 · 状态：✅ 部署产物就绪 · 待产品负责人执行服务器部署
> 目标：将 Beta 后端部署到腾讯云香港轻量服务器
> 原则：P0 冻结，禁止新增功能/改用户流程/改埋点逻辑
> ⚠️ 本阶段**不实际购买服务器 / 不自动上线 / 不进入 Beta 分发**

---

## 一、部署产物（deploy/ 目录）

| 文件 | 说明 | 状态 |
|------|------|:---:|
| `deploy/start_server.py` | 生产启动入口（CORS + 环境变量映射） | ✅ 验证通过 |
| `deploy/requirements_prod.txt` | 生产依赖（精简） | ✅ |
| `deploy/nginx_atlas.conf` | Nginx HTTPS 反向代理 | ✅ |
| `deploy/backup_sqlite.sh` | SQLite 每日备份 | ✅ |
| `deploy/.env.example` | 环境变量示例（不含真实密钥） | ✅ |
| `release/Atlas_v491_Cloud_Data_Init.md` | 数据初始化方案 | ✅ |

### start_server.py 验证
- ✅ FastAPI 启动入口与本地一致（同一 router）
- ✅ CORSMiddleware 已加载
- ✅ 环境变量映射：`WX_APPID→WECHAT_APPID`、`WX_APPSECRET→WECHAT_APPSECRET`、`DATABASE_PATH→ATLAS_STORAGE_DIR`
- ✅ 生产默认 `WECHAT_LOGIN_MOCK=0` / `WECHAT_MOCK=0`
- ✅ 零硬编码密钥

---

## 二、服务器部署步骤（完整命令，产品负责人执行）

### 1. 系统更新
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Python 环境
```bash
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git curl
python3.11 --version
```

### 3. 创建虚拟环境 + 上传代码
```bash
sudo mkdir -p /opt/atlas && sudo chown $USER /opt/atlas
cd /opt/atlas
# 上传: backend/ engine/ deploy/ requirements.txt（scp/rsync 或 git clone）
git clone <你的仓库> atlas   # 或 scp -r 上传
cd atlas
python3.11 -m venv venv
source venv/bin/activate
```

### 4. 安装依赖
```bash
pip install --upgrade pip
pip install -r deploy/requirements_prod.txt
```

### 5. 配置 .env
```bash
sudo mkdir -p /opt/atlas/data
cp deploy/.env.example .env
# 编辑 .env 填真实 WX_APPSECRET（⚠️ 勿提交 Git）
```

### 6. 启动 FastAPI（测试）
```bash
cd /opt/atlas/atlas
set -a; source ../.env; set +a   # 或 export 各变量
source venv/bin/activate
python deploy/start_server.py      # 监听 127.0.0.1:8000
# 另开终端验证:
curl http://127.0.0.1:8000/healthz
```

### 7. 配置 systemd（守护进程）
```bash
sudo tee /etc/systemd/system/atlas.service > /dev/null <<'EOF'
[Unit]
Description=Atlas Mobile MVP API
After=network.target

[Service]
User=$USER
WorkingDirectory=/opt/atlas/atlas
EnvironmentFile=/opt/atlas/.env
ExecStart=/opt/atlas/atlas/venv/bin/python /opt/atlas/atlas/deploy/start_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now atlas
sudo systemctl status atlas
```

### 8. 配置 Nginx
```bash
sudo cp deploy/nginx_atlas.conf /etc/nginx/sites-available/atlas
sudo ln -s /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 9. HTTPS 准备
```bash
# 腾讯云 SSL 控制台申请免费 DV 证书 → 下载 → 放到:
sudo mkdir -p /etc/nginx/ssl/api.atlas-lottery.com
# 上传 fullchain.pem / key.pem → 确认 nginx_atlas.conf 路径一致
sudo nginx -t && sudo systemctl reload nginx
```

### 10. 防火墙
```bash
sudo ufw allow 22/tcp     # SSH（建议白名单）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 三、数据初始化（首次启动前）

按 `release/Atlas_v491_Cloud_Data_Init.md`：
- 上传 `mobile_mvp.db`（含 1702 期开奖）到 `/opt/atlas/data/`
- 执行初始化脚本清空 users/tickets/reminders/events（保留 draws）
- 首次启动检查 6 项

---

## 四、安全检查

| 项 | 确认 |
|----|------|
| **AppSecret 不进 Git** | ✅ 只在服务器 `.env`（`.env.example` 无真实值） |
| **日志脱敏** | ✅ 不记录 openid/session_key/secret |
| **SQLite 备份路径** | ✅ `/opt/atlas/backups`，每日 cron（保留 14 天） |
| **SSH 安全** | ✅ ufw 22 白名单 + 密钥登录（禁用密码） |
| **数据库不暴露公网** | ✅ uvicorn 只监听 127.0.0.1，Nginx 转发 |
| **生产 mock 关闭** | ✅ `WECHAT_LOGIN_MOCK=0` / `WECHAT_MOCK=0` |

---

## 五、部署后验证清单

- [ ] `https://api.atlas-lottery.com/healthz` → 200
- [ ] `https://.../api/mobile/v1/draws/latest?lottery=dlt` → 26088
- [ ] 小程序后台配置 request 合法域名 `https://api.atlas-lottery.com`
- [ ] 真机登录 → U0001 is_new=True → 再次 is_new=False
- [ ] 录票 → ticket_saved 落库

---

## 六、红线确认

- ✅ 未新增功能 / 未改用户流程 / 未改埋点逻辑
- ✅ 未购买服务器 / 未自动上线 / 未进入 Beta 分发（等待审核）
- ✅ 零硬编码密钥

---

## 七、待产品负责人决策

> **部署执行需你操作（购买服务器/域名/备案），本阶段仅准备产物。**
> 确认后我可协助：上传步骤排查 / 报错处理 / 首次启动检查。
