# Atlas v4.9.1 — 微信登录集成报告（Wechat Login Integration Report）

> 阶段：Beta 前置 · 目的：接入真实微信用户身份体系，为 Beta-0 提供可信留存数据
> 状态：✅ 完成 · 测试 167 passed 零回归

---

## 一、修改文件

| 文件 | 修改 | 性质 |
|------|------|------|
| `backend/mobile/wechat.py` | 新增 `WeChatLoginClient`（code2session） | 后端登录 |
| `backend/mobile/api.py` | 新增 `auth_router` + `/api/auth/wechat/login` 路由 | 后端登录 |
| `mobile_app/utils/api.js` | 新增 `wechatLogin(code)` | 前端登录 |
| `mobile_app/pages/onboarding/index.js` | `start()` 改用 `wx.login` → 后端登录（移除 demo_openid） | 前端登录 |
| `tests/v492/test_wechat_login.py` | 新增 16 个登录测试 | 测试 |

**未修改**：页面结构 / 彩票逻辑 / 埋点事件集 / 数据库结构 / 订阅消息逻辑。

---

## 二、数据流程

```
小程序 onboarding
   ├─ wx.login() → 获取临时 code
   └─ POST /api/auth/wechat/login {code}

后端
   ├─ WeChatLoginClient.code2session(code)
   │    ├─ mock 模式（无密钥）：code → mock_openid_xxx
   │    └─ 真实模式：调微信 jscode2session → openid
   ├─ 查询 users 表（openid 唯一）
   │    ├─ 已存在 → 返回原 U_ID（is_new=False）+ mobile_opened 事件
   │    └─ 不存在 → 创建新用户分配 U_ID（is_new=True）+ install_completed 事件
   └─ 返回 {user_id, openid, is_new}
```

**身份绑定**：
- openid 唯一（`uq_mobile_user_openid` 约束）
- U_ID 永久（创建后不变）
- 同一微信用户：第一次 U0001，第二次仍 U0001 ✅

---

## 三、安全检查

| 项 | 实现 |
|----|------|
| **AppSecret 存储** | 仅环境变量 `WECHAT_APPSECRET`，**零硬编码** |
| **AppID 存储** | 环境变量 `WECHAT_APPID` |
| **Git 安全** | 未提交任何密钥到仓库（`git diff` 验证无密钥） |
| **日志安全** | 登录接口不输出 openid/session_key/secret 到日志 |
| **mock 兜底** | 无密钥时 mock 模式（`WECHAT_LOGIN_MOCK=1`），不阻塞测试/联调 |
| **输入校验** | code 必填（pydantic），空 code 422 拒绝 |
| **错误处理** | code 无效 → 401，不创建脏用户 |

> ✅ 提交前已用 `git grep -i secret/appsecret` 确认仓库无密钥。

---

## 四、测试结果

| # | 用例 | 结果 |
|---|------|:---:|
| 1 | 登录成功（code → 用户） | ✅ |
| 2 | code 失败处理（空 code 422 / 缺失 422） | ✅ |
| 3 | openid 不存在 → 创建用户 | ✅ |
| 4 | openid 存在 → 返回旧用户（5 次登录同一 U_ID） | ✅ |
| 5 | 用户隔离（不同 code → 不同 U_ID） | ✅ |
| 6 | 原 Beta 埋点不受影响（events/tickets/冻结指标） | ✅ |

**v492 全量：167 passed（151 原 + 16 新），零回归。**

---

## 五、Beta 影响分析

| 影响 | 分析 |
|------|------|
| **留存可信度** | ✅ 真实 openid 使「用户是否回来」可统计，D1/D3/D7 有意义 |
| **用户去重** | ✅ 同一微信用户多次进入 = 同一 U_ID，不再重复计新用户 |
| **首次建档率** | ✅ install_completed 只在新用户首登触发，分母准确 |
| **体验版验证** | ⚠️ 需重新上传体验版（前端登录逻辑变更） |
| **原有 demo_openid 用户** | ⚠️ U0001/U0002（demo）不会被真实登录识别——Beta 开始前建议清空测试用户，从真实登录重新建档 |
| **后端部署** | ⚠️ 需配置环境变量 `WECHAT_APPID` + `WECHAT_APPSECRET` 后重启（产品负责人提供 AppSecret） |

---

## 六、部署配置（产品负责人执行）

```bash
set WECHAT_APPID=wxe254d2aded63ca94
set WECHAT_APPSECRET=<你的AppSecret>
set WECHAT_LOGIN_MOCK=0
```

> ⚠️ AppSecret 从微信公众平台 → 开发 → 开发管理 → 开发设置 获取。
> 配置后重启后端 uvicorn + 重新上传体验版。

---

## 七、红线确认

- ✅ 未新增业务功能（登录是身份体系，非彩票功能）
- ✅ 未修改彩票逻辑 / 页面结构 / 埋点事件集
- ✅ 未提交任何真实 AppSecret 到代码仓库
