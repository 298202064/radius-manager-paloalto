from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.schemas.gateway import (
    GatewayCreate, GatewayUpdate, GatewayResponse, GatewayPage,
    GatewayOnlineUserList, GatewayOnlineUser,
)
from app.services.gateway_service import GatewayService
from app.utils.pagination import PaginationParams

router = APIRouter(
    prefix="/gateways",
    tags=["只读网关"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=GatewayPage)
async def list_gateways(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = GatewayService(db)
    pagination = PaginationParams(page, page_size)
    gateways, total = await service.get_gateways(pagination)
    items = [GatewayResponse.model_validate(g) for g in gateways]
    return GatewayPage(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=GatewayResponse, status_code=status.HTTP_201_CREATED)
async def create_gateway(data: GatewayCreate, db: AsyncSession = Depends(get_db)):
    service = GatewayService(db)
    gateway = await service.create_gateway(data)
    return GatewayResponse.model_validate(gateway)


@router.get("/online-users", response_model=GatewayOnlineUserList)
async def get_gateway_online_users(db: AsyncSession = Depends(get_db)):
    """Fetch online users from all enabled PAN-OS gateways."""
    service = GatewayService(db)
    gateways = await service.get_enabled_gateways()
    all_users: list[GatewayOnlineUser] = []

    for gw in gateways:
        try:
            password = service.get_decrypted_password(gw)
            users = await fetch_panos_online_users(gw.host, gw.username, password)
            for u in users:
                u.gateway_name = gw.name
                u.gateway_host = gw.host
            all_users.extend(users)
        except Exception as e:
            # Log error but continue with other gateways
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to fetch online users from {gw.name} ({gw.host}): {e}")

    return GatewayOnlineUserList(items=all_users, total=len(all_users))


@router.post("/{gateway_id}/test")
async def test_gateway_connection(
    gateway_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Test connection to a specific gateway."""
    service = GatewayService(db)
    gateway = await service.get_gateway_by_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=404, detail="只读网关不存在")

    try:
        password = service.get_decrypted_password(gateway)
        users = await fetch_panos_online_users(gateway.host, gateway.username, password)
        return {"status": "success", "message": f"连接成功，当前在线用户数: {len(users)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/{gateway_id}", response_model=GatewayResponse)
async def get_gateway(gateway_id: int, db: AsyncSession = Depends(get_db)):
    service = GatewayService(db)
    gateway = await service.get_gateway_by_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=404, detail="只读网关不存在")
    return GatewayResponse.model_validate(gateway)


@router.put("/{gateway_id}", response_model=GatewayResponse)
async def update_gateway(
    gateway_id: int, data: GatewayUpdate, db: AsyncSession = Depends(get_db)
):
    service = GatewayService(db)
    gateway = await service.get_gateway_by_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=404, detail="只读网关不存在")
    gateway = await service.update_gateway(gateway, data)
    return GatewayResponse.model_validate(gateway)


@router.delete("/{gateway_id}")
async def delete_gateway(gateway_id: int, db: AsyncSession = Depends(get_db)):
    service = GatewayService(db)
    gateway = await service.get_gateway_by_id(gateway_id)
    if gateway is None:
        raise HTTPException(status_code=404, detail="只读网关不存在")
    await service.delete_gateway(gateway)
    return {"message": "只读网关已删除"}


async def fetch_panos_online_users(
    host: str, username: str, password: str
) -> list[GatewayOnlineUser]:
    """Fetch GlobalProtect online users from a PAN-OS firewall via API."""
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET
    import ssl
    import logging

    from app.utils.network import validate_gateway_host

    logger = logging.getLogger(__name__)

    # Defense-in-depth: validate host again at the point of use
    try:
        host = validate_gateway_host(host)
    except ValueError as e:
        raise Exception(f"网关主机地址验证失败: {e}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    base_url = host.rstrip("/")
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    # Step 1: Get API key
    key_url = (
        f"{base_url}/api/?type=keygen"
        f"&user={urllib.parse.quote(username)}"
        f"&password={urllib.parse.quote(password)}"
    )
    try:
        resp = urllib.request.urlopen(key_url, timeout=15, context=ctx)
        body = resp.read()
        root = ET.fromstring(body)
        status = root.get("status", "")
        if status != "success":
            raise Exception(f"API keygen failed: status={status}")

        api_key = root.findtext(".//key", "")
        if not api_key:
            raise Exception("No API key in response")
    except Exception as e:
        raise Exception(f"Failed to get API key: {e}")

    # Step 2: Fetch online users
    cmd = (
        "<show><global-protect-gateway>"
        "<current-user></current-user>"
        "</global-protect-gateway></show>"
    )
    query_url = (
        f"{base_url}/api/?type=op"
        f"&cmd={urllib.parse.quote(cmd)}"
        f"&key={urllib.parse.quote(api_key)}"
    )

    try:
        resp = urllib.request.urlopen(query_url, timeout=15, context=ctx)
        body = resp.read()
        root = ET.fromstring(body)
        status = root.get("status", "")
        if status != "success":
            raise Exception(f"API query failed: status={status}")

        result = root.find("result")
        if result is None:
            return []

        users = []
        for entry in result.findall("entry"):
            user = GatewayOnlineUser(
                username=entry.findtext("username", ""),
                computer=entry.findtext("computer", ""),
                client_os=entry.findtext("client", ""),
                virtual_ip=entry.findtext("virtual-ip", ""),
                public_ip=entry.findtext("public-ip", ""),
                login_time=entry.findtext("login-time", ""),
                tunnel_type=entry.findtext("tunnel-type", ""),
            )
            if user.username:
                users.append(user)

        return users
    except Exception as e:
        raise Exception(f"Failed to fetch online users: {e}")
