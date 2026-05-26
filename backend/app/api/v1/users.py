from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPage, PasswordReset
from app.schemas.otp import OTPStatusResponse
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/users", tags=["用户管理"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=UserPage)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="搜索用户名或邮箱"),
    enabled: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    pagination = PaginationParams(page, page_size)
    users, total = await service.get_users(pagination, search, enabled)

    items = []
    for u in users:
        has_otp = await service.has_otp_enabled(u.id)
        resp = UserResponse.model_validate(u)
        resp.has_otp = has_otp
        items.append(resp)

    return UserPage(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    existing = await service.get_user_by_username(data.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = await service.create_user(data)
    has_otp = await service.has_otp_enabled(user.id)
    resp = UserResponse.model_validate(user)
    resp.has_otp = has_otp
    return resp


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    has_otp = await service.has_otp_enabled(user.id)
    resp = UserResponse.model_validate(user)
    resp.has_otp = has_otp
    return resp


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user = await service.update_user(user, data)
    has_otp = await service.has_otp_enabled(user.id)
    resp = UserResponse.model_validate(user)
    resp.has_otp = has_otp
    return resp


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    await service.delete_user(user)
    return {"message": "用户已删除"}


@router.put("/{user_id}/reset-password")
async def reset_password(
    user_id: int, data: PasswordReset, db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    await service.update_user(user, UserUpdate(password=data.new_password))
    return {"message": "密码已重置"}


@router.get("/{user_id}/otp-status", response_model=OTPStatusResponse)
async def get_user_otp_status(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    from sqlalchemy import select
    from app.models.otp_device import OTPDevice
    result = await db.execute(
        select(OTPDevice).where(OTPDevice.user_id == user_id)
    )
    device = result.scalar_one_or_none()

    return OTPStatusResponse(
        enabled=device.enabled if device else False,
        device_name=device.device_name if device else "default",
        has_device=device is not None,
    )


@router.delete("/{user_id}/otp")
async def admin_disable_user_otp(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    from app.models.otp_device import OTPDevice
    await db.execute(
        delete(OTPDevice).where(OTPDevice.user_id == user_id)
    )
    return {"message": "用户的OTP已解除绑定"}
