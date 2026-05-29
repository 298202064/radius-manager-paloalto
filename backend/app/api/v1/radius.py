import ipaddress
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password
from app.models.radacct import RadAcct
from app.models.user import User
from app.models.otp_device import OTPDevice
from app.schemas.otp import RADIUSAuthRequest
from app.services.otp_service import OTPService


def _parse_allowed_networks(csv_str: str) -> list:
    """Parse RADIUS_ALLOWED_IPS into a list of ip_network/ip_address objects."""
    nets = []
    for entry in csv_str.split(","):
        entry = entry.strip()
        if not entry:
            continue
        try:
            nets.append(ipaddress.ip_network(entry, strict=False))
        except ValueError:
            nets.append(ipaddress.ip_address(entry))
    return nets


_RADIUS_NETS = _parse_allowed_networks(settings.radius_allowed_ips)


async def verify_radius_source(request: Request):
    """Dependency: ensure the RADIUS request originates from an allowed IP/net."""
    client_ip_str = request.client.host if request.client else "0.0.0.0"
    try:
        client_ip = ipaddress.ip_address(client_ip_str)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid client IP")

    for net in _RADIUS_NETS:
        if isinstance(net, ipaddress.IPv4Network | ipaddress.IPv6Network):
            if client_ip in net:
                return
        elif client_ip == net:
            return

    raise HTTPException(status_code=403, detail="Access denied")


class AccountingRequest(BaseModel):
    acct_session_id: str
    acct_unique_id: Optional[str] = ""
    username: Optional[str] = ""
    nas_ip_address: str = "0.0.0.0"
    acct_status_type: str = ""
    acct_start_time: Optional[str] = None
    acct_stop_time: Optional[str] = None
    acct_input_octets: Optional[int] = None
    acct_output_octets: Optional[int] = None
    acct_input_gigawords: Optional[int] = None
    acct_output_gigawords: Optional[int] = None
    acct_session_time: Optional[int] = None
    acct_terminate_cause: Optional[str] = None
    called_station_id: Optional[str] = None
    calling_station_id: Optional[str] = None
    service_type: Optional[str] = None
    framed_protocol: Optional[str] = None
    framed_ip_address: Optional[str] = None
    nas_port_id: Optional[str] = None
    nas_port_type: Optional[str] = None
    connect_info: Optional[str] = None


router = APIRouter(
    prefix="/radius",
    tags=["RADIUS内部"],
    dependencies=[Depends(verify_radius_source)],
)


@router.post("/authenticate")
async def radius_authenticate(
    request: RADIUSAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    RADIUS OTP authentication endpoint.
    Called by FreeRADIUS rlm_rest module for OTP users.
    """
    username = request.username
    password = request.password

    # Find user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None or not user.enabled:
        return JSONResponse(
            status_code=401,
            content={"result": "reject", "message": "用户不存在或已被禁用"},
        )

    # Check if user has OTP enabled
    result = await db.execute(
        select(OTPDevice).where(
            OTPDevice.user_id == user.id,
            OTPDevice.enabled == True,
        )
    )
    otp_device = result.scalar_one_or_none()

    if otp_device:
        if len(password) <= 6:
            # Challenge response: password contains just the 6-digit OTP code.
            # Static password was already validated by FreeRADIUS PAP in round 1.
            try:
                decrypted_secret = OTPService.decrypt_otp_secret(otp_device.secret)
                if not OTPService.verify_totp(decrypted_secret, password):
                    return JSONResponse(
                        status_code=401,
                        content={"result": "reject", "message": "OTP验证码错误"},
                    )
            except Exception:
                return JSONResponse(
                    status_code=401,
                    content={"result": "reject", "message": "OTP验证失败"},
                )

            otp_device.last_used_at = datetime.now(timezone.utc)
            await db.flush()

            return {
                "result": "accept",
                "message": "认证成功（OTP二次验证）",
                "attributes": {},
            }
        else:
            # Direct mode: password is "static_password" + "6-digit-totp"
            static_pass = password[:-6]
            otp_code = password[-6:]

            # Verify static password
            if not verify_password(static_pass, user.password_hash):
                return JSONResponse(
                    status_code=401,
                    content={"result": "reject", "message": "密码错误"},
                )

            # Verify OTP code
            try:
                decrypted_secret = OTPService.decrypt_otp_secret(otp_device.secret)
                if not OTPService.verify_totp(decrypted_secret, otp_code):
                    return JSONResponse(
                        status_code=401,
                        content={"result": "reject", "message": "OTP验证码错误"},
                    )
            except Exception:
                return JSONResponse(
                    status_code=401,
                    content={"result": "reject", "message": "OTP验证失败"},
                )

            otp_device.last_used_at = datetime.now(timezone.utc)
            await db.flush()

            return {
                "result": "accept",
                "message": "认证成功（含OTP）",
                "attributes": {},
            }
    else:
        # Non-OTP user: standard password verification
        if not verify_password(password, user.password_hash):
            return JSONResponse(
                status_code=401,
                content={"result": "reject", "message": "密码错误"},
            )

        return {
            "result": "accept",
            "message": "认证成功",
            "attributes": {},
        }


@router.post("/accounting", include_in_schema=False)
async def radius_accounting(
    request: AccountingRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    RADIUS accounting relay endpoint.
    Called by FreeRADIUS acct_relay rest module.
    Persists accounting data to radacct table.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Accounting request: status=%s user=%s nas=%s",
                request.acct_status_type, request.username, request.nas_ip_address)

    status_type = request.acct_status_type

    try:
        if status_type == "Start":
            # Parse start time
            start_time = None
            if request.acct_start_time:
                try:
                    start_time = datetime.fromisoformat(request.acct_start_time)
                except (ValueError, TypeError):
                    start_time = datetime.now(timezone.utc)

            acct = RadAcct(
                acctsessionid=request.acct_session_id,
                acctuniqueid=request.acct_unique_id or "",
                username=request.username,
                nasipaddress=request.nas_ip_address,
                acctstarttime=start_time or datetime.now(timezone.utc),
                acctupdatetime=datetime.now(timezone.utc),
                calledstationid=request.called_station_id,
                callingstationid=request.calling_station_id,
                servicetype=request.service_type,
                framedprotocol=request.framed_protocol,
                framedipaddress=request.framed_ip_address,
                nasportid=request.nas_port_id,
                nasporttype=request.nas_port_type,
                connectinfo_start=request.connect_info,
            )
            db.add(acct)
            await db.flush()
            logger.info("Accounting Start recorded: session=%s user=%s",
                        request.acct_session_id, request.username)

        elif status_type == "Stop":
            stop_time = None
            if request.acct_stop_time:
                try:
                    stop_time = datetime.fromisoformat(request.acct_stop_time)
                except (ValueError, TypeError):
                    stop_time = datetime.now(timezone.utc)

            # Find matching session and update
            stmt = (
                select(RadAcct)
                .where(RadAcct.acctsessionid == request.acct_session_id)
                .where(RadAcct.acctstoptime.is_(None))
                .order_by(RadAcct.radacctid.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            acct = result.scalar_one_or_none()

            if acct:
                # Calculate input/output with gigawords
                input_octets = request.acct_input_octets or 0
                output_octets = request.acct_output_octets or 0
                if request.acct_input_gigawords:
                    input_octets += request.acct_input_gigawords * (2**32)
                if request.acct_output_gigawords:
                    output_octets += request.acct_output_gigawords * (2**32)

                acct.acctstoptime = stop_time or datetime.now(timezone.utc)
                acct.acctupdatetime = datetime.now(timezone.utc)
                acct.acctinputoctets = input_octets
                acct.acctoutputoctets = output_octets
                acct.acctterminatecause = request.acct_terminate_cause
                acct.acctinterval = request.acct_session_time
                acct.connectinfo_stop = request.connect_info
                await db.flush()
                logger.info("Accounting Stop recorded: session=%s user=%s duration=%s",
                            request.acct_session_id, request.username, request.acct_session_time)
            else:
                # No open session found, insert a completed record
                acct = RadAcct(
                    acctsessionid=request.acct_session_id,
                    acctuniqueid=request.acct_unique_id or "",
                    username=request.username,
                    nasipaddress=request.nas_ip_address,
                    acctstoptime=stop_time or datetime.now(timezone.utc),
                    acctupdatetime=datetime.now(timezone.utc),
                    acctinputoctets=request.acct_input_octets,
                    acctoutputoctets=request.acct_output_octets,
                    acctterminatecause=request.acct_terminate_cause,
                    acctinterval=request.acct_session_time,
                    calledstationid=request.called_station_id,
                    callingstationid=request.calling_station_id,
                )
                db.add(acct)
                await db.flush()
                logger.info("Accounting Stop (orphan): session=%s user=%s",
                            request.acct_session_id, request.username)

        elif status_type == "Interim-Update":
            input_octets = request.acct_input_octets or 0
            output_octets = request.acct_output_octets or 0
            if request.acct_input_gigawords:
                input_octets += request.acct_input_gigawords * (2**32)
            if request.acct_output_gigawords:
                output_octets += request.acct_output_gigawords * (2**32)

            stmt = (
                select(RadAcct)
                .where(RadAcct.acctsessionid == request.acct_session_id)
                .where(RadAcct.acctstoptime.is_(None))
                .order_by(RadAcct.radacctid.desc())
                .limit(1)
            )
            result = await db.execute(stmt)
            acct = result.scalar_one_or_none()

            if acct:
                acct.acctupdatetime = datetime.now(timezone.utc)
                acct.acctinputoctets = input_octets
                acct.acctoutputoctets = output_octets
                acct.acctinterval = request.acct_session_time
                if request.called_station_id:
                    acct.calledstationid = request.called_station_id
                if request.calling_station_id:
                    acct.callingstationid = request.calling_station_id
                if request.framed_ip_address:
                    acct.framedipaddress = request.framed_ip_address
                await db.flush()
            else:
                # No open session, insert as new
                acct = RadAcct(
                    acctsessionid=request.acct_session_id,
                    acctuniqueid=request.acct_unique_id or "",
                    username=request.username,
                    nasipaddress=request.nas_ip_address,
                    acctstarttime=datetime.now(timezone.utc),
                    acctupdatetime=datetime.now(timezone.utc),
                    acctinputoctets=input_octets,
                    acctoutputoctets=output_octets,
                    acctinterval=request.acct_session_time,
                    calledstationid=request.called_station_id,
                    callingstationid=request.calling_station_id,
                )
                db.add(acct)
                await db.flush()

            logger.info("Accounting Update recorded: session=%s user=%s",
                        request.acct_session_id, request.username)

        else:
            logger.warning("Unknown accounting status type: %s", status_type)

    except Exception as e:
        logger.error("Failed to persist accounting record: %s", e)

    return JSONResponse(status_code=200, content={"status": "ok"})
