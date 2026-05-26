from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.schemas.ldap import (
    LDAPConfigCreate, LDAPConfigUpdate, LDAPConfigResponse, LDAPConfigPage,
    LDAPSearchRequest, LDAPSearchResponse, LDAPImportRequest, LDAPImportResult,
)
from app.services.ldap_service import LDAPService
from app.utils.pagination import PaginationParams

router = APIRouter(
    prefix="/ldap",
    tags=["LDAP导入"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/configs", response_model=LDAPConfigPage)
async def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = LDAPService(db)
    pagination = PaginationParams(page, page_size)
    configs, total = await service.get_configs(pagination)
    items = [LDAPConfigResponse.model_validate(c) for c in configs]
    return LDAPConfigPage(items=items, total=total, page=page, page_size=page_size)


@router.post("/configs", response_model=LDAPConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(data: LDAPConfigCreate, db: AsyncSession = Depends(get_db)):
    service = LDAPService(db)
    cfg = await service.create_config(data)
    return LDAPConfigResponse.model_validate(cfg)


@router.get("/configs/{config_id}", response_model=LDAPConfigResponse)
async def get_config(config_id: int, db: AsyncSession = Depends(get_db)):
    service = LDAPService(db)
    cfg = await service.get_config_by_id(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LDAP 配置不存在")
    return LDAPConfigResponse.model_validate(cfg)


@router.put("/configs/{config_id}", response_model=LDAPConfigResponse)
async def update_config(
    config_id: int, data: LDAPConfigUpdate, db: AsyncSession = Depends(get_db)
):
    service = LDAPService(db)
    cfg = await service.get_config_by_id(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LDAP 配置不存在")
    cfg = await service.update_config(cfg, data)
    return LDAPConfigResponse.model_validate(cfg)


@router.delete("/configs/{config_id}")
async def delete_config(config_id: int, db: AsyncSession = Depends(get_db)):
    service = LDAPService(db)
    cfg = await service.get_config_by_id(config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LDAP 配置不存在")
    await service.delete_config(cfg)
    return {"message": "LDAP 配置已删除"}


@router.post("/configs/{config_id}/test")
async def test_connection(config_id: int, db: AsyncSession = Depends(get_db)):
    service = LDAPService(db)
    try:
        result = await service.test_connection(config_id)
        return result
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.post("/configs/{config_id}/search", response_model=LDAPSearchResponse)
async def search_ad_users(
    config_id: int,
    data: LDAPSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    service = LDAPService(db)
    try:
        items = await service.search_users(
            config_id,
            search_filter=data.search_filter,
            search_base=data.search_base,
        )
        return LDAPSearchResponse(items=items, total=len(items))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/configs/{config_id}/import", response_model=LDAPImportResult)
async def import_ad_users(
    config_id: int,
    data: LDAPImportRequest,
    db: AsyncSession = Depends(get_db),
):
    service = LDAPService(db)
    try:
        result = await service.import_users(config_id, data.usernames)
        return LDAPImportResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
