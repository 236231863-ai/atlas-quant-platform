"""User workspace API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from backend.service.user_service import UserService, UserData, WorkspaceData, ProjectData

router = APIRouter(tags=["users"])
_svc = UserService()

@router.post("/users")
async def create_user(user: UserData): return _svc.create_user(user)
@router.get("/users")
async def list_users(): return _svc.list_users()
@router.get("/users/{uid}")
async def get_user(uid: str):
    u = _svc.get_user(uid)
    if not u: raise HTTPException(404, "User not found")
    return u
@router.post("/workspaces")
async def create_workspace(ws: WorkspaceData): return _svc.create_workspace(ws)
@router.get("/users/{uid}/workspaces")
async def list_workspaces(uid: str): return _svc.list_workspaces(uid)
@router.post("/projects")
async def create_project(p: ProjectData): return _svc.create_project(p)
