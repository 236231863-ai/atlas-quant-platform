"""backend.mobile.api - Mobile MVP FastAPI 路由（/api/mobile/v1）。

路由：
  POST /users/auth        微信授权登录（openid → user_id）
  POST /tickets           录票
  GET  /tickets           我的票
  POST /draws/check       核对一张票
  GET  /draws/latest      最新开奖
  POST /reminders         创建开奖提醒
  POST /reminders/click   提醒点击回执
  GET  /funnel            用户漏斗
  POST /events            埋点上报
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.mobile.db import MobileDB
from backend.mobile.service import MobileService
from backend.mobile.wechat import WeChatLoginClient, WeChatReminderClient

router = APIRouter(prefix="/api/mobile/v1", tags=["mobile"])
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

# 模块级 DB（默认真实文件；测试可通过 api._db = MobileDB.in_memory() 替换）
_db = MobileDB.file_based()


def reset_db(db: Optional[MobileDB] = None) -> MobileDB:
    """替换模块级 DB（测试用）。"""
    global _db
    _db = db or MobileDB.in_memory()
    return _db


def get_db() -> MobileDB:
    return _db


def get_service() -> MobileService:
    return MobileService(_db.session())


# ---- Schema ----
class AuthRequest(BaseModel):
    openid: str = Field(..., min_length=4, max_length=64)
    lottery_type: str = "大乐透"
    purchase_frequency: str = "每周"


class TicketRequest(BaseModel):
    user_id: str
    lottery: str = "dlt"
    text: str
    buy_date: str = ""
    draw_date: str = ""


class DrawCheckRequest(BaseModel):
    user_id: str
    ticket_id: str
    issue: str


class ReminderRequest(BaseModel):
    user_id: str
    ticket_id: str
    issue: str
    remind_at: str = ""


class ReminderClickRequest(BaseModel):
    reminder_id: str


class WechatLoginRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=128)
    lottery_type: str = "大乐透"
    purchase_frequency: str = "每周"


class EventRequest(BaseModel):
    event_name: str
    user_id: str
    source: str = "MOBILE"
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---- Routes ----
@auth_router.post("/wechat/login")
def wechat_login(req: WechatLoginRequest, svc: MobileService = Depends(get_service)):
    """真实微信登录：wx.login code → code2session → openid → 查/建用户。

    - openid 已存在 → 返回原 U_ID（同一微信用户稳定身份）
    - openid 不存在 → 创建新用户并分配 U_ID
    """
    client = WeChatLoginClient()
    result = client.code2session(req.code)
    if not result.get("ok") or not result.get("openid"):
        raise HTTPException(status_code=401, detail=result.get("errmsg", "code_invalid"))
    openid = result["openid"]
    user = svc.users.get_by_openid(openid)
    is_new = user is None
    if user is None:
        lottery_type, frequency = svc._normalize(req.lottery_type, req.purchase_frequency)
        user = svc.users.create(openid, lottery_type, frequency)
        svc.track("install_completed", user.user_id, source="MOBILE")
    else:
        svc.track("mobile_opened", user.user_id, source="MOBILE")
    return {
        "user_id": user.user_id,
        "openid": openid,
        "is_new": is_new,
        "mock": result.get("mock", False),
    }


@router.post("/users/auth")
def auth_user(req: AuthRequest, svc: MobileService = Depends(get_service)):
    user = svc.register_or_get(req.openid, req.lottery_type, req.purchase_frequency)
    svc.track("app_install" if user.first_open_at == user.registered_at else "app_open",
              user.user_id, source="MOBILE")
    return {"user_id": user.user_id, "first_ticket_saved": bool(user.first_ticket_saved_at)}


@router.post("/tickets")
def create_ticket(req: TicketRequest, svc: MobileService = Depends(get_service)):
    try:
        result = svc.save_ticket(req.user_id, req.lottery, req.text,
                                 req.buy_date, req.draw_date)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return result


@router.get("/tickets")
def list_tickets(user_id: str, svc: MobileService = Depends(get_service)):
    return svc.list_tickets(user_id)


@router.post("/draws/check")
def check_draw(req: DrawCheckRequest, svc: MobileService = Depends(get_service)):
    result = svc.check_ticket(req.user_id, req.ticket_id, req.issue)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("reason", "not_found"))
    return result


@router.get("/draws/latest")
def latest_draw(lottery: str = "dlt", svc: MobileService = Depends(get_service)):
    draw = svc.latest_draw(lottery)
    if draw is None:
        raise HTTPException(status_code=404, detail="draw_not_found")
    return draw


@router.post("/reminders")
def create_reminder(req: ReminderRequest, svc: MobileService = Depends(get_service)):
    result = svc.create_reminder(req.user_id, req.ticket_id, req.issue, req.remind_at)
    # 验证阶段：下发 mock 微信消息
    client = WeChatReminderClient()
    dispatch = client.send_draw_reminder("", req.issue, req.remind_at)
    result["wechat"] = dispatch
    return result


@router.post("/reminders/click")
def reminder_click(req: ReminderClickRequest, svc: MobileService = Depends(get_service)):
    return {"ok": svc.mark_reminder_clicked(req.reminder_id)}


@router.get("/funnel")
def funnel(svc: MobileService = Depends(get_service)):
    return svc.funnel()


@router.post("/events")
def track_event(req: EventRequest, svc: MobileService = Depends(get_service)):
    ok = svc.track(req.event_name, req.user_id, req.source, req.metadata)
    if not ok:
        raise HTTPException(status_code=422, detail="unknown_event")
    return {"ok": True}
