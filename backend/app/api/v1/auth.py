from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.utils.ratelimit import RateLimiter

router = APIRouter(prefix="/auth", tags=["认证"])

_login_limiter = RateLimiter("auth:login", max_requests=5, window_seconds=60)
_refresh_limiter = RateLimiter("auth:refresh", max_requests=10, window_seconds=60)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(_login_limiter),
):
    auth_service = AuthService(db)
    user = await auth_service.authenticate(request.username, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return await auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(_refresh_limiter),
):
    auth_service = AuthService(db)
    result = await auth_service.refresh_access_token(request.refresh_token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期",
        )
    return result


@router.post("/logout")
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    await auth_service.logout(request.refresh_token)
    return {"message": "已登出"}
