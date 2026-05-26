import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.schemas.nas_client import (
    NASClientCreate, NASClientUpdate, NASClientResponse, NASClientPage
)
from app.services.nas_service import NASService
from app.utils.pagination import PaginationParams
from app.utils.radclient_config import generate_clients_conf

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/nas-clients", tags=["NAS客户端"], dependencies=[Depends(get_current_admin)]
)


async def _sync_to_freeradius(db: AsyncSession, raise_on_error: bool = False):
    """Generate clients.conf, write to shared mount, and send HUP to FreeRADIUS.

    If raise_on_error is False, errors are logged but not raised (used for auto-sync
    after CRUD operations). If True, HTTPException is raised (used for manual sync).
    """
    service = NASService(db)
    clients = await service.get_enabled_clients()
    config_text = generate_clients_conf(clients)

    config_path = "/app/sync/clients.conf"
    try:
        with open(config_path, "w") as f:
            f.write(config_text)
        logger.info("Written clients.conf (%d clients) to %s", len(clients), config_path)
    except Exception as e:
        logger.error("Failed to write clients.conf: %s", e)
        if raise_on_error:
            raise HTTPException(status_code=500, detail=f"写入配置文件失败: {e}")
        return

    import docker

    try:
        docker_client = docker.from_env()
    except Exception as e:
        logger.error("Docker connection failed: %s", e)
        if raise_on_error:
            raise HTTPException(status_code=500, detail=f"无法连接 Docker: {e}")
        return

    try:
        container = docker_client.containers.get("radius-freeradius")
    except Exception as e:
        logger.error("Container radius-freeradius not found: %s", e)
        if raise_on_error:
            raise HTTPException(status_code=500, detail="找不到 FreeRADIUS 容器")
        return

    try:
        container.kill(signal="HUP")
        logger.info("Sent HUP signal to radius-freeradius")
    except Exception as e:
        logger.error("Failed to reload FreeRADIUS: %s", e)
        if raise_on_error:
            raise HTTPException(status_code=500, detail=f"重载 FreeRADIUS 失败: {e}")
        return

    return clients


@router.get("", response_model=NASClientPage)
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = NASService(db)
    pagination = PaginationParams(page, page_size)
    clients, total = await service.get_clients(pagination)
    items = []
    for c in clients:
        resp = NASClientResponse.model_validate(c)
        resp.has_secret = bool(c.secret)
        items.append(resp)
    return NASClientPage(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=NASClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(data: NASClientCreate, db: AsyncSession = Depends(get_db)):
    service = NASService(db)
    client = await service.create_client(data)
    resp = NASClientResponse.model_validate(client)
    resp.has_secret = True
    # Auto-sync after create
    await _sync_to_freeradius(db)
    return resp


@router.get("/generate-config", response_class=PlainTextResponse)
async def generate_config(db: AsyncSession = Depends(get_db)):
    service = NASService(db)
    clients = await service.get_enabled_clients()
    return generate_clients_conf(clients)


@router.post("/sync")
async def sync_config(db: AsyncSession = Depends(get_db)):
    """Manual sync: generate clients.conf, write to FreeRADIUS, and reload."""
    result = await _sync_to_freeradius(db, raise_on_error=True)
    clients = result or []
    return {
        "message": f"配置已同步，已应用 {len(clients)} 个客户端，FreeRADIUS 已重载",
        "clients_count": len(clients),
    }


@router.get("/{client_id}", response_model=NASClientResponse)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db)):
    service = NASService(db)
    client = await service.get_client_by_id(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="NAS客户端不存在")
    resp = NASClientResponse.model_validate(client)
    resp.has_secret = bool(client.secret)
    return resp


@router.put("/{client_id}", response_model=NASClientResponse)
async def update_client(
    client_id: int, data: NASClientUpdate, db: AsyncSession = Depends(get_db)
):
    service = NASService(db)
    client = await service.get_client_by_id(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="NAS客户端不存在")
    client = await service.update_client(client, data)
    resp = NASClientResponse.model_validate(client)
    resp.has_secret = bool(client.secret)
    # Auto-sync after update
    await _sync_to_freeradius(db)
    return resp


@router.delete("/{client_id}")
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db)):
    service = NASService(db)
    client = await service.get_client_by_id(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="NAS客户端不存在")
    await service.delete_client(client)
    # Auto-sync after delete
    await _sync_to_freeradius(db)
    return {"message": "NAS客户端已删除"}
