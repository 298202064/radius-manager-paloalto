from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.schemas.log import DashboardStats
from app.services.log_service import LogService
from app.services.gateway_service import GatewayService
from app.api.v1.gateways import fetch_panos_online_users

router = APIRouter(prefix="/dashboard", tags=["仪表盘"], dependencies=[Depends(get_current_admin)])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    service = LogService(db)
    stats = await service.get_dashboard_stats()

    # Get real online user count from configured VPN gateways
    gw_service = GatewayService(db)
    gateways = await gw_service.get_enabled_gateways()
    total_gw_online = 0
    for gw in gateways:
        try:
            password = gw_service.get_decrypted_password(gw)
            users = await fetch_panos_online_users(gw.host, gw.username, password)
            total_gw_online += len(users)
        except Exception:
            pass

    stats["active_users_online"] = total_gw_online
    return DashboardStats(**stats)
