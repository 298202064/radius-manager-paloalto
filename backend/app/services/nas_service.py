from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nas_client import NASClient
from app.schemas.nas_client import NASClientCreate, NASClientUpdate
from app.utils.encryption import encrypt_secret
from app.utils.pagination import PaginationParams


class NASService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_clients(
        self, pagination: PaginationParams
    ) -> tuple[list[NASClient], int]:
        # Total
        count_result = await self.db.execute(select(func.count()).select_from(NASClient))
        total = count_result.scalar() or 0

        # Items
        result = await self.db.execute(
            select(NASClient).order_by(NASClient.id.desc())
            .offset(pagination.offset).limit(pagination.limit)
        )
        clients = list(result.scalars().all())
        return clients, total

    async def get_client_by_id(self, client_id: int) -> NASClient | None:
        result = await self.db.execute(select(NASClient).where(NASClient.id == client_id))
        return result.scalar_one_or_none()

    async def create_client(self, data: NASClientCreate) -> NASClient:
        encrypted_secret = encrypt_secret(data.secret)
        client = NASClient(
            shortname=data.shortname,
            ip_address=data.ip_address,
            secret=encrypted_secret,
            radsecret=data.secret,
            nas_type=data.nas_type,
            description=data.description,
            enabled=data.enabled,
        )
        self.db.add(client)
        await self.db.flush()
        return client

    async def update_client(self, client: NASClient, data: NASClientUpdate) -> NASClient:
        update_data = data.model_dump(exclude_unset=True)

        if "secret" in update_data and update_data["secret"]:
            client.secret = encrypt_secret(update_data["secret"])
            client.radsecret = update_data["secret"]
            del update_data["secret"]

        for field, value in update_data.items():
            setattr(client, field, value)

        await self.db.flush()
        return client

    async def delete_client(self, client: NASClient) -> None:
        await self.db.delete(client)

    async def get_enabled_clients(self) -> list[NASClient]:
        result = await self.db.execute(
            select(NASClient).where(NASClient.enabled == True)
        )
        return list(result.scalars().all())
