from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.core.deps import get_current_admin
from app.schemas.dynamic_list import DynamicListUpdate, DynamicListResponse
from app.services import dynamic_list_service

router = APIRouter(prefix="/dynamic-lists", tags=["动态列表"], dependencies=[Depends(get_current_admin)])


@router.get("/ip", response_model=DynamicListResponse)
async def get_ip_list():
    lines = dynamic_list_service.get_ip_list()
    return DynamicListResponse(lines=lines, total=len(lines))


@router.put("/ip", response_model=DynamicListResponse)
async def update_ip_list(data: DynamicListUpdate):
    lines = dynamic_list_service.set_ip_list(data.lines)
    return DynamicListResponse(lines=lines, total=len(lines))


@router.get("/url", response_model=DynamicListResponse)
async def get_url_list():
    lines = dynamic_list_service.get_url_list()
    return DynamicListResponse(lines=lines, total=len(lines))


@router.put("/url", response_model=DynamicListResponse)
async def update_url_list(data: DynamicListUpdate):
    lines = dynamic_list_service.set_url_list(data.lines)
    return DynamicListResponse(lines=lines, total=len(lines))
