from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gateway import ReadonlyGateway
from app.schemas.gateway import GatewayCreate, GatewayUpdate
from app.utils.encryption import encrypt_secret, decrypt_secret
from app.utils.pagination import PaginationParams


class GatewayService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_gateways(
        self, pagination: PaginationParams
    ) -> tuple[list[ReadonlyGateway], int]:
        count_result = await self.db.execute(
            select(func.count()).select_from(ReadonlyGateway)
        )
        total = count_result.scalar() or 0

        result = await self.db.execute(
            select(ReadonlyGateway).order_by(ReadonlyGateway.id.desc())
            .offset(pagination.offset).limit(pagination.limit)
        )
        gateways = list(result.scalars().all())
        return gateways, total

    async def get_gateway_by_id(self, gateway_id: int) -> ReadonlyGateway | None:
        result = await self.db.execute(
            select(ReadonlyGateway).where(ReadonlyGateway.id == gateway_id)
        )
        return result.scalar_one_or_none()

    async def create_gateway(self, data: GatewayCreate) -> ReadonlyGateway:
        encrypted_password = encrypt_secret(data.password)
        gateway = ReadonlyGateway(
            name=data.name,
            host=data.host,
            username=data.username,
            password=encrypted_password,
            description=data.description,
            enabled=data.enabled,
        )
        self.db.add(gateway)
        await self.db.flush()
        return gateway

    async def update_gateway(
        self, gateway: ReadonlyGateway, data: GatewayUpdate
    ) -> ReadonlyGateway:
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            gateway.password = encrypt_secret(update_data["password"])
            del update_data["password"]

        for field, value in update_data.items():
            setattr(gateway, field, value)

        await self.db.flush()
        return gateway

    async def delete_gateway(self, gateway: ReadonlyGateway) -> None:
        await self.db.delete(gateway)

    async def get_enabled_gateways(self) -> list[ReadonlyGateway]:
        result = await self.db.execute(
            select(ReadonlyGateway).where(ReadonlyGateway.enabled == True)
        )
        return list(result.scalars().all())

    @staticmethod
    def get_decrypted_password(gateway: ReadonlyGateway) -> str:
        """Get decrypted password for a gateway."""
        return decrypt_secret(gateway.password)
