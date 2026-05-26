from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.nas_clients import router as nas_clients_router
from app.api.v1.logs import router as logs_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.self_service import router as self_service_router
from app.api.v1.radius import router as radius_router
from app.api.v1.gateways import router as gateways_router
from app.api.v1.ldap import router as ldap_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(nas_clients_router)
api_router.include_router(logs_router)
api_router.include_router(dashboard_router)
api_router.include_router(self_service_router)
api_router.include_router(radius_router)
api_router.include_router(gateways_router)
api_router.include_router(ldap_router)
