# Atlas v4.9.1 — Beta 体验二维码生成流程（Beta QR Code Flow）

> 目的：生成一个可分享的二维码，种子用户扫码直达小程序邀请页
> 落地页：`pages/invite/index`（邀请页）

---

## 一、方案对比

| 方案 | 方式 | 适用 |
|------|------|------|
| **A. 官方小程序码**（推荐） | 微信公众平台生成 | 体验版/正式版 |
| **B. 接口生成** | `wxacode.get` API | 需 access_token |
| C. 普通链接二维码 | 任意二维码工具 | 不适合（小程序需识别） |

> 验证阶段推荐 **方案 A**（无需写代码，后台直接生成）。

---

## 二、方案 A：官方后台生成（体验版）

1. 进入 [微信公众平台](https://mp.weixin.qq.com) → 管理 → 版本管理
2. 找到当前「体验版」
3. 点「生成小程序码」（或「下载体验二维码」）
4. 选择落地路径：`pages/invite/index`
5. 下载 PNG → 保存到 `release/assets/beta_qr.png`

**注意**：体验版二维码只有**体验成员**（已添加的 10 人）扫码才能进入。

---

## 三、方案 B：接口生成（可选）

需要：`access_token`（AppID+Secret 换取）

```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=SECRET
```

获取 token 后调用小程序码接口：

```
POST https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=TOKEN
Body: { "scene": "beta0", "page": "pages/invite/index", "check_path": false }
```

返回图片二进制 → 保存为 PNG。

---

## 四、二维码信息卡（随码一起发）

```
🎫 Atlas 彩票管家 · Beta 体验
📱 扫码进入（需在 Beta 体验成员名单）
👉 3 分钟：录一张票 → 开提醒 → 等开奖
```

---

## 五、分发渠道

| 渠道 | 方式 |
|------|------|
| 微信私聊 | 发二维码图片 + 邀请话术 |
| 彩票群 | 发二维码 + 群公告 |
| 线下 | 打印二维码（彩票店/朋友） |

---

## 六、验证二维码

- 用产品负责人微信（已加体验成员）扫码
- 应落地 `pages/invite/index` 邀请页
- 非体验成员扫码 → 提示无权限（正常）

---

## 七、二维码更新

- 体验版每次重新上传后，二维码重新生成
- 正式版发布后，用正式版二维码替换

---

## 八、二维码资产清单

| 文件 | 说明 |
|------|------|
| `release/assets/beta_qr.png` | 体验版二维码（待产品负责人生成后存放） |
| `release/assets/beta_invite_card.png` | 邀请卡（二维码 + 文案，可选） |
