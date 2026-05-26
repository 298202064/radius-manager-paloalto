from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.schemas.log import AuthLogPage, AuthLogEntry, OnlineUserPage, OnlineUserEntry
from app.services.log_service import LogService
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/logs", tags=["日志"], dependencies=[Depends(get_current_admin)])


@router.get("/auth", response_model=AuthLogPage)
async def list_auth_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    username: str = Query("", description="按用户名筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    result: str = Query("", description="认证结果: Access-Accept / Access-Reject"),
    db: AsyncSession = Depends(get_db),
):
    service = LogService(db)
    pagination = PaginationParams(page, page_size)
    logs, total = await service.get_auth_logs(
        pagination, username, start_date, end_date, result
    )
    items = [AuthLogEntry.model_validate(log) for log in logs]
    return AuthLogPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/online", response_model=OnlineUserPage)
async def list_online_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = LogService(db)
    pagination = PaginationParams(page, page_size)
    users, total = await service.get_online_users(pagination)
    items = [OnlineUserEntry.model_validate(u) for u in users]
    return OnlineUserPage(items=items, total=total, page=page, page_size=page_size)
