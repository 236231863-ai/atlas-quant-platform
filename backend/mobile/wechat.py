"""backend.mobile.wechat - 微信接口（登录 + 订阅消息，验证用途）。

设计：
- 登录：code2session 换取 openid（Beta 前置，真实微信身份）
- 提醒：订阅消息下发（验证 mock 优先）
- 安全：AppID/AppSecret 只从环境变量读取（WECHAT_APPID / WECHAT_APPSECRET），
  禁止写入代码/Git/配置文件/日志

真实 API 参考：
  GET https://api.weixin.qq.com/sns/jscode2session?appid=&secret=&js_code=&grant_type=authorization_code
  POST https://api.weixin.qq.com/cgi-bin/message/subscribe/send
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Dict, Optional


class WeChatLoginClient:
    """微信登录：code → openid（code2session）。

    安全：
      - AppID/AppSecret 从环境变量读取（WECHAT_APPID / WECHAT_APPSECRET）
      - 未配置时进入 mock 模式（code 形如 mock_xxx → openid mock_openid_xxx），
        便于测试与无密钥联调
    """

    def __init__(self, appid: Optional[str] = None, appsecret: Optional[str] = None):
        self._appid = appid or os.environ.get("WECHAT_APPID", "")
        self._appsecret = appsecret or os.environ.get("WECHAT_APPSECRET", "")
        self._mock = os.environ.get("WECHAT_LOGIN_MOCK", "1") == "1"

    @property
    def is_mock(self) -> bool:
        return self._mock or not (self._appid and self._appsecret)

    def code2session(self, code: str) -> Dict:
        """用 wx.login 的 code 换 openid。

        返回：{ok, openid, errcode, errmsg, mock}
        - mock 模式：code='mock_<suffix>' → openid='mock_openid_<suffix>'
        - 真实模式：调微信 jscode2session API
        """
        if self.is_mock:
            suffix = code.replace("mock_", "") if code.startswith("mock_") else code[:20] or "unknown"
            return {"ok": True, "openid": f"mock_openid_{suffix}", "errcode": 0, "errmsg": "mock", "mock": True}

        params = urllib.parse.urlencode({
            "appid": self._appid,
            "secret": self._appsecret,
            "js_code": code,
            "grant_type": "authorization_code",
        })
        url = f"https://api.weixin.qq.com/sns/jscode2session?{params}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # 网络异常
            return {"ok": False, "openid": "", "errcode": -2, "errmsg": str(e), "mock": False}
        if "openid" in data:
            return {"ok": True, "openid": data["openid"], "errcode": 0, "errmsg": "", "mock": False}
        return {"ok": False, "openid": "", "errcode": data.get("errcode", -1),
                "errmsg": data.get("errmsg", ""), "mock": False}


class WeChatReminderClient:
    """微信订阅消息客户端。"""

    def __init__(self, appid: Optional[str] = None, secret: Optional[str] = None,
                 template_id: Optional[str] = None):
        # 从环境变量读取，缺省进入验证模式
        self._appid = appid or os.environ.get("WECHAT_APPID", "")
        self._secret = secret or os.environ.get("WECHAT_SECRET", "")
        self._template_id = template_id or os.environ.get("WECHAT_TEMPLATE_ID", "")
        self._mock = os.environ.get("WECHAT_MOCK", "1") == "1"

    @property
    def is_mock(self) -> bool:
        return self._mock or not (self._appid and self._secret and self._template_id)

    def _get_access_token(self) -> str:
        """获取 access_token（真实模式下）。"""
        if self.is_mock:
            return "mock_access_token"
        url = (
            "https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={self._appid}&secret={self._secret}"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("access_token", "")

    def send_draw_reminder(self, openid: str, issue: str,
                           draw_date: str, lottery_name: str = "大乐透") -> Dict:
        """下发开奖提醒订阅消息。

        返回 {ok, errcode, errmsg, mock}。mock 模式下固定 ok=True。
        """
        if self.is_mock:
            return {"ok": True, "errcode": 0, "errmsg": "mock", "mock": True}

        token = self._get_access_token()
        if not token:
            return {"ok": False, "errcode": -1, "errmsg": "access_token_failed", "mock": False}

        payload = {
            "touser": openid,
            "template_id": self._template_id,
            "page": "pages/draw_result/index",
            "data": {
                "thing1": {"value": f"{lottery_name}开奖提醒"},
                "character_string2": {"value": issue},
                "time3": {"value": draw_date},
            },
            "miniprogram_state": "formal",
        }
        url = (
            "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"
            f"?access_token={token}"
        )
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": data.get("errcode") == 0,
            "errcode": data.get("errcode", -1),
            "errmsg": data.get("errmsg", ""),
            "mock": False,
        }


class ReminderDispatcher:
    """提醒调度：扫描未发送提醒 → 调用微信客户端下发 → 标记 sent + 记录事件。

    v4.9.1 P4.5 数据链路修复：
      发送成功 → 记录 reminder_sent 行为事件（behavior_events）
      发送失败 → 保留未发送状态（下次重试），不丢提醒
    """

    def __init__(self, wechat: WeChatReminderClient, reminder_repo,
                 user_repo, event_repo=None):
        self._wechat = wechat
        self._reminders = reminder_repo
        self._users = user_repo
        self._events = event_repo  # 可选：BehaviorEventRepository

    def dispatch_all(self) -> Dict[str, int]:
        """下发所有未发送提醒，返回 {sent, failed}。"""
        sent = 0
        failed = 0
        for r in self._reminders.list_unsent():
            user = self._users.get(r.user_id)
            openid = user.openid if user else ""
            result = self._wechat.send_draw_reminder(openid, r.issue, r.remind_at)
            if result.get("ok"):
                self._reminders.mark_sent(r.id)
                if self._events is not None:
                    self._events.record(
                        "reminder_sent", r.user_id, source="MOBILE",
                        metadata={"reminder_id": r.id, "issue": r.issue},
                    )
                sent += 1
            else:
                failed += 1
        return {"sent": sent, "failed": failed}
