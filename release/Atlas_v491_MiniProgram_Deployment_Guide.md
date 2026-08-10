# Atlas v4.9.1 — 微信小程序部署指南（Mini Program Deployment Guide）

> 阶段：Beta Distribution · 目的：让 10 名种子用户能通过二维码进入小程序
> 前置：`mobile_app/` 目录（已验证）· 后端 `backend/mobile/`（已验证）

---

## 一、部署总览

```
微信公众平台注册小程序 → 导入 mobile_app → 配置后端 → 上传体验版
   → 生成小程序码 → 分发二维码给种子用户
```

---

## 二、步骤 1：注册微信小程序

1. 打开 [微信公众平台](https://mp.weixin.qq.com) → 注册 → 选择「小程序」
2. 用邮箱注册 + 个人主体（验证阶段可用个人）
3. 注册后获取 **AppID**（开发设置 → 开发信息）
4. 记录：`AppID`、`AppSecret`（开发设置 → 重置可得）

> ⚠️ 个人主体小程序不能开通支付/部分能力，但**订阅消息**可用（验证阶段足够）。

---

## 三、步骤 2：导入项目

1. 下载安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开 → 导入项目：
   - 目录：`mobile_app/`
   - AppID：填入上一步的 AppID
3. 修改 `project.config.json` 的 `appid`

```json
{ "appid": "wx你的AppID" }
```

4. 工具内点「编译」，本地预览通过（6 页面 + 邀请页可切换）

---

## 四、步骤 3：配置后端

### 启动后端（本机/云服务器）
```bash
cd "C:/Users/Administrator/Documents/Codex/2026-07-28/lqrp-v0-1-v0-2-v0/AtlasQuant"
PYTHONIOENCODING=utf-8 python -c "
import uvicorn
from fastapi import FastAPI
from backend.mobile.api import router
app = FastAPI(title='Atlas Mobile MVP API')
app.include_router(router)
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### 小程序连接后端
修改 `mobile_app/utils/api.js` 的 `BASE`：
```js
const BASE = 'https://你的域名/api/mobile/v1'  // 或 http://局域网IP:8000
```

> ⚠️ 微信小程序正式/体验版**要求 HTTPS**。验证阶段可：
> - 开发者工具勾选「不校验合法域名」本地调试
> - 或配置 HTTPS 域名（云服务器 + SSL 证书）
> - 或局域网 IP 本地联调（同一 WiFi）

---

## 五、步骤 4：订阅消息模板（开奖提醒）

1. 微信公众平台 → 功能 → 订阅消息 → 公共模板库
2. 搜索「开奖提醒」类模板（或用 `thing` + `character_string` + `time` 组合）
3. 选用后获取 **模板 ID**
4. 后端配置环境变量：
```bash
set WECHAT_APPID=你的AppID
set WECHAT_SECRET=你的AppSecret
set WECHAT_TEMPLATE_ID=你的模板ID
set WECHAT_MOCK=0
```

> 验证阶段可保持 `WECHAT_MOCK=1`（mock 下发），不依赖真实推送。

---

## 六、步骤 5：上传体验版

1. 开发者工具 → 点「上传」→ 填版本号（如 0.1.0）→ 备注
2. 微信公众平台 → 管理 → 版本管理 → 选「体验版」
3. 添加体验成员（10 名种子用户的微信）：
   - 管理 → 成员管理 → 体验成员 → 添加

---

## 七、步骤 6：生成小程序码（体验版）

1. 微信公众平台 → 版本管理 → 体验版 → 点「生成小程序码」
2. 落地页选 `pages/invite/index`（邀请页）
3. 下载二维码图片 → 保存 `release/assets/beta_qr.png`

> 详见《Beta 体验二维码生成流程》。

---

## 八、发布前自检清单

| 项 | 检查 |
|----|------|
| AppID 已替换 | `project.config.json` |
| 后端可访问 | 用浏览器/curl 测 `/api/mobile/v1/funnel` |
| 6 页面可导航 | 开发者工具编译通过 |
| 协议页正常 | 首屏协议可勾选可进入 |
| 录票成功 | 录一张真实号码保存 |
| 埋点落库 | `mobile_behavior_events` 有记录 |

---

## 九、故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 请求失败 errno 600001 | 域名未配置/未校验 | 勾选不校验合法域名（调试）或配 HTTPS |
| 无法保存票 | 后端未启动/网络 | 检查 uvicorn 运行 |
| 订阅消息没收到 | mock 模式/模板未配 | 保持 mock（验证）或配模板 |
| 页面白屏 | 页面路径错 | 检查 app.json pages 顺序 |
