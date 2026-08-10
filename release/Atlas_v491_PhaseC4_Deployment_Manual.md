# Atlas v4.9.1 — Phase C.4 服务器执行手册（Deployment Manual）

> 用途：产品负责人在腾讯云香港 Ubuntu 22.04 服务器上**逐段复制执行**本手册
> 前置：已购买轻量服务器 + 域名 + 已 ssh 登录
> 部署包：`release/assets/atlas_mobile_deploy.tar.gz`（backend + deploy，34.5KB）

---

## Phase 1 环境初始化

```bash
# 1.1 Ubuntu 版本
lsb_release -a
# 预期: Ubuntu 22.04 LTS

# 1.2 Python 版本
python3 --version
# 若 < 3.11:
sudo apt update && sudo apt install -y python3.11 python3.11-venv

# 1.3 Git
git --version

# 1.4 防火墙（先查后开，防锁 SSH）
sudo ufw status
# 若 enable 后需确保 22 已放行：
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
sudo ufw enable

# 1.5 SSH 安全（可选强化）
# 编辑 /etc/ssh/sshd_config: PasswordAuthentication no
# sudo systemctl restart sshd
```

---

## Phase 2 项目部署

```bash
# 2.1 目录 + 上传代码
sudo mkdir -p /opt/atlas && sudo chown $USER /opt/atlas
cd /opt/atlas
# 上传部署包（在本地电脑执行）:
#   scp release/assets/atlas_mobile_deploy.tar.gz root@<服务器IP>:/opt/atlas/
tar -xzf atlas_mobile_deploy.tar.gz
# 此时 /opt/atlas 下有 backend/ + deploy/

# 2.2 数据目录
mkdir -p /opt/atlas/data

# 2.3 虚拟环境
cd /opt/atlas
python3.11 -m venv venv
source venv/bin/activate

# 2.4 安装依赖
pip install --upgrade pip
pip install -r deploy/requirements_prod.txt

# 2.5 配置 .env（⚠️ 填真实密钥，勿提交 Git）
cp deploy/.env.example .env
nano .env
# 填入:
#   WX_APPID=wxe254d2aded63ca94
#   WX_APPSECRET=<你的AppSecret>
#   DATABASE_PATH=/opt/atlas/data
#   WECHAT_LOGIN_MOCK=0
#   WECHAT_MOCK=0

# 2.6 验证环境变量（不打印密钥值）
source .env
echo "APPID=$WX_APPID  DB=$DATABASE_PATH  MOCK=$WECHAT_LOGIN_MOCK"
```

---

## Phase 3 数据初始化

```bash
# 3.1 上传本地数据库（含 1702 期开奖）
# 本地执行:
#   scp ~/.atlas/mobile_mvp.db root@<服务器IP>:/opt/atlas/data/

# 3.2 初始化（保留 draws，清空用户/票/提醒/事件/反馈）
cd /opt/atlas && source venv/bin/activate && source .env
PYTHONIOENCODING=utf-8 python -c "
import os, sqlite3
db = os.path.join(os.environ['DATABASE_PATH'], 'mobile_mvp.db')
conn = sqlite3.connect(db); cur = conn.cursor()
cur.execute('DELETE FROM mobile_users')
cur.execute('DELETE FROM mobile_tickets')
cur.execute('DELETE FROM mobile_reminders')
cur.execute('DELETE FROM mobile_behavior_events')
conn.commit()
cur.execute('SELECT COUNT(*) FROM mobile_draws'); print('保留 draws:', cur.fetchone()[0])
for t in ['mobile_users','mobile_tickets','mobile_reminders','mobile_behavior_events']:
    cur.execute(f'SELECT COUNT(*) FROM {t}'); print(f'{t} 清空后:', cur.fetchone()[0])
conn.close()
"
```

---

## Phase 4 FastAPI 上线（systemd）

```bash
# 4.1 先手动测通
cd /opt/atlas && source venv/bin/activate && source .env
python deploy/start_server.py &
sleep 3
curl -s http://127.0.0.1:8000/healthz
# 预期: {"status":"ok"}
kill %1

# 4.2 systemd 服务
sudo tee /etc/systemd/system/atlas.service > /dev/null <<'EOF'
[Unit]
Description=Atlas Mobile MVP API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/atlas
EnvironmentFile=/opt/atlas/.env
ExecStart=/opt/atlas/venv/bin/python /opt/atlas/deploy/start_server.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/atlas.log
StandardError=append:/var/log/atlas.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now atlas
sudo systemctl status atlas
# 预期: active (running)
tail -20 /var/log/atlas.log
```

> 自动启动 ✅（enable）· 崩溃恢复 ✅（Restart=always）· 日志路径明确 ✅（/var/log/atlas.log）

---

## Phase 5 Nginx + HTTPS

```bash
# 5.1 Nginx
sudo apt install -y nginx
sudo cp deploy/nginx_atlas.conf /etc/nginx/sites-available/atlas
sudo sed -i 's/api.atlas-lottery.com/你的域名/g' /etc/nginx/sites-available/atlas
sudo ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 5.2 HTTPS 证书（腾讯云 DV）
# 控制台申请免费证书 → 下载 → 上传到:
sudo mkdir -p /etc/nginx/ssl/你的域名
# scp fullchain.pem key.pem 到该目录
sudo nginx -t && sudo systemctl reload nginx

# 5.3 检查（本地 curl 带域名的 HTTPS）
curl -s https://你的域名/health
# 预期 200: {"status":"ok"}
```

> 链路：HTTP 80 → 301 HTTPS → Nginx → 127.0.0.1:8000 FastAPI

---

## Phase 6 微信小程序连接

**仅修改 `mobile_app/utils/api.js` 的 BASE_URL（第 5 行）**

```js
// 从
const BASE = 'http://192.168.31.95:8000/api/mobile/v1'
// 改为
const BASE = 'https://你的域名/api/mobile/v1'
```

```bash
# 小程序后台配置 request 合法域名:
#   微信公众平台 → 开发 → 开发管理 → 开发设置 → 服务器域名
#   request 合法域名 添加: https://你的域名
# 重新上传体验版
```

> ⚠️ 其他代码一律不改。

---

## Phase 7 验证

| # | 验证 | 方法 | 预期 |
|---|------|------|------|
| 1 | 小程序打开 | 真机扫码体验版 | 邀请页正常 |
| 2 | 微信登录 | 点开始使用 | U0001 is_new=True |
| 3 | 新用户生成 | 后台查 mobile_users | registered=1 |
| 4 | 录入彩票 | 录一张票 | ticket_saved 事件 |
| 5 | 查询开奖 | 开奖结果页 | 26088 显示 |
| 6 | 提醒创建 | 开提醒 | reminder_enabled |
| 7 | 数据写入云端 | 查 /opt/atlas/data/mobile_mvp.db | 有数据 |

```bash
# 云端数据检查
cd /opt/atlas && source venv/bin/activate
PYTHONIOENCODING=utf-8 python -c "
import os, sqlite3
db = os.path.join(os.environ['DATABASE_PATH'], 'mobile_mvp.db')
conn = sqlite3.connect(db); cur = conn.cursor()
for t in ['mobile_users','mobile_tickets','mobile_behavior_events']:
    cur.execute(f'SELECT COUNT(*) FROM {t}'); print(f'{t}:', cur.fetchone()[0])
conn.close()
"
```

---

## 备份（每日）

```bash
chmod +x deploy/backup_sqlite.sh
(crontab -l 2>/dev/null; echo "0 3 * * * DATABASE_PATH=/opt/atlas/data /opt/atlas/deploy/backup_sqlite.sh") | crontab -
```

---

## 红线

- ✅ 不新增功能 / 不改产品逻辑 / 不改埋点 / 不改数据库结构 / 不加商业功能
- ✅ 密钥只在服务器 .env，不进 Git
- ✅ 不自动邀请用户（等 Beta 分发审核）
