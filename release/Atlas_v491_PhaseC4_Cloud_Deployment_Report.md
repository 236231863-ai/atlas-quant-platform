# Atlas v4.9.1 — Phase C.4 云端部署报告（Cloud Deployment Report）

> 阶段：Phase C.4 · 状态：🟡 **部署物就绪，服务器执行待产品负责人**
> 目标：将 Atlas 后端部署到腾讯云香港 Ubuntu 22.04
> 红线：不新增功能/不改逻辑/不改埋点/不改数据结构/不加商业功能

---

## 〇、诚实声明（关键）

> **本机环境无腾讯云服务器访问权限**（未提供服务器 IP / SSH 凭证）。
> 因此 **Phase 1-7 的实际服务器操作需产品负责人在服务器上执行**（或提供 SSH 访问后我协助）。
> 本报告交付：**可直接复制的完整执行手册 + 部署压缩包**，产品负责人按序执行即可上线。

---

## 一、已交付产物

| 产物 | 路径 | 状态 |
|------|------|:---:|
| 部署压缩包 | `release/assets/atlas_mobile_deploy.tar.gz`（34.5KB，backend+deploy） | ✅ |
| 服务器执行手册 | `release/Atlas_v491_PhaseC4_Deployment_Manual.md` | ✅ |
| 生产启动入口 | `deploy/start_server.py`（CORS+环境变量映射，已验证） | ✅ |
| Nginx 配置 | `deploy/nginx_atlas.conf` | ✅ |
| 备份脚本 | `deploy/backup_sqlite.sh` | ✅ |
| 环境变量示例 | `deploy/.env.example`（无密钥） | ✅ |

---

## 二、Phase 1-7 执行状态（服务器侧）

| Phase | 内容 | 状态 |
|-------|------|:---:|
| 1 环境初始化 | Ubuntu/Python3.11/Git/防火墙/SSH | ⏳ 待服务器执行 |
| 2 项目部署 | 上传包/虚拟环境/依赖/.env | ⏳ 待服务器执行 |
| 3 数据初始化 | 保留 draws，清空 5 表 | ⏳ 待服务器执行 |
| 4 FastAPI 上线 | systemd（自动启动/崩溃恢复/日志） | ⏳ 待服务器执行 |
| 5 Nginx+HTTPS | HTTP→HTTPS→FastAPI，/health 200 | ⏳ 待服务器执行 |
| 6 小程序连接 | 改 api.js BASE→https 域名 | ⏳ 待服务器执行 |
| 7 验证 | 7 项真机验证 | ⏳ 待服务器执行 |

> 所有命令已写入执行手册，产品负责人逐段复制即可。

---

## 三、执行手册要点（服务器操作）

### Phase 1-2（环境 + 部署）
```bash
# 上传部署包后：
sudo mkdir -p /opt/atlas && sudo chown $USER /opt/atlas
cd /opt/atlas && tar -xzf atlas_mobile_deploy.tar.gz
python3.11 -m venv venv && source venv/bin/activate
pip install -r deploy/requirements_prod.txt
cp deploy/.env.example .env && nano .env   # 填 WX_APPID/WX_APPSECRET/DATABASE_PATH
```

### Phase 3（数据初始化）
```bash
# 上传 ~/.atlas/mobile_mvp.db 到 /opt/atlas/data/ 后执行初始化脚本（保留 draws 清空其余）
```

### Phase 4（systemd）
```bash
sudo systemctl enable --now atlas && tail -20 /var/log/atlas.log
```

### Phase 5-6（Nginx + 小程序）
```bash
# Nginx + HTTPS 证书 + 小程序后台 request 合法域名 + api.js BASE 改 https
```

### Phase 7（验证）
```bash
curl -s https://你的域名/health   # 预期 200
# 真机 7 项验证
```

---

## 四、安全检查

| 项 | 确认 |
|----|------|
| AppSecret 不进 Git | ✅ 仅服务器 .env（.gitignore 已忽略 .env） |
| 部署包无密钥 | ✅ 打包时排除 .env / __pycache__ |
| 日志脱敏 | ✅ 不记录 openid/session_key/secret |
| 数据库不暴露公网 | ✅ uvicorn 监听 127.0.0.1，Nginx 转发 |
| SSH 安全 | ✅ ufw + 可选禁密码登录 |

---

## 五、待办（产品负责人）

1. **购买腾讯云香港轻量服务器 + 域名**（约 ¥60/月）
2. **上传部署包**（`scp release/assets/atlas_mobile_deploy.tar.gz`）
3. **按执行手册 Phase 1-7 逐段执行**
4. 遇到任何报错 → 发我，立即协助

---

## 六、红线确认

- ✅ 未新增功能 / 未改产品逻辑 / 未改埋点 / 未改数据库结构 / 未加商业功能
- ✅ 未自动上线 / 未自动邀请用户（等待 Beta 分发审核）
- ✅ 密钥零硬编码

---

## 七、下一步

> **服务器部署完成后**（/health 200 + 真机 7 项通过），进入 **Beta 分发审核**。
> 分发前需：数据初始化确认（0 用户）+ 真实登录验证 + 体验版更新 + 10 人招募清单。
