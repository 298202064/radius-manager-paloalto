from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.models.user import User
from app.models.otp_device import OTPDevice
from app.schemas.user import ChangePasswordRequest
from app.schemas.otp import OTPBindRequest, OTPStatusResponse, OTPQRResponse
from app.services.user_service import UserService
from app.services.otp_service import OTPService

router = APIRouter(prefix="/self", tags=["自助服务"])


@router.put("/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码错误")

    service = UserService(db)
    from app.schemas.user import UserUpdate
    await service.update_user(
        current_user, UserUpdate(password=request.new_password)
    )
    return {"message": "密码修改成功"}


@router.get("/otp/qrcode", response_model=OTPQRResponse)
async def get_otp_qrcode(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get QR code for binding a new OTP device."""
    secret = OTPService.generate_secret()
    data = OTPService.create_device_data(secret, current_user.username)

    # Remove any previous unbound devices
    await db.execute(
        delete(OTPDevice).where(
            OTPDevice.user_id == current_user.id,
            OTPDevice.enabled == False,
        )
    )

    # Persist the new device (disabled until verified via bind endpoint)
    encrypted_secret = OTPService.encrypt_otp_secret(secret)
    device = OTPDevice(
        user_id=current_user.id,
        secret=encrypted_secret,
        enabled=False,
    )
    db.add(device)
    await db.flush()

    return OTPQRResponse(**data)


@router.post("/otp/bind")
async def bind_otp(
    request: OTPBindRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bind OTP device after verifying the current TOTP code."""
    # Check if user already has an enabled OTP device
    result = await db.execute(
        select(OTPDevice).where(
            OTPDevice.user_id == current_user.id,
            OTPDevice.enabled == True,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="OTP已经绑定，请先解绑再重新绑定")

    # Get the most recent unbound device
    result = await db.execute(
        select(OTPDevice).where(
            OTPDevice.user_id == current_user.id,
            OTPDevice.enabled == False,
        ).order_by(OTPDevice.id.desc())
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=400, detail="请先获取二维码")

    # Verify the TOTP code
    decrypted_secret = OTPService.decrypt_otp_secret(device.secret)
    if not OTPService.verify_totp(decrypted_secret, request.token):
        raise HTTPException(status_code=400, detail="验证码错误，请重试")

    device.enabled = True
    await db.flush()
    return {"message": "OTP绑定成功"}


@router.delete("/otp")
async def unbind_otp(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unbind OTP device."""
    await db.execute(
        delete(OTPDevice).where(OTPDevice.user_id == current_user.id)
    )
    return {"message": "OTP已解除绑定"}


@router.get("/otp/status", response_model=OTPStatusResponse)
async def get_otp_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(OTPDevice).where(OTPDevice.user_id == current_user.id)
    )
    device = result.scalar_one_or_none()

    return OTPStatusResponse(
        enabled=device.enabled if device else False,
        device_name=device.device_name if device else "default",
        has_device=device is not None,
    )
