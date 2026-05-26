from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.radpostauth import RadPostAuth
from app.models.radacct import RadAcct
from app.utils.pagination import PaginationParams


class LogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_auth_logs(
        self,
        pagination: PaginationParams,
        username: str = "",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        result: str = "",
    ) -> tuple[list[RadPostAuth], int]:
        conditions = []
        if username:
            conditions.append(RadPostAuth.username.ilike(f"%{username}%"))
        if start_date:
            conditions.append(RadPostAuth.authdate >= start_date)
        if end_date:
            conditions.append(RadPostAuth.authdate <= end_date)
        if result:
            conditions.append(RadPostAuth.reply == result)

        query = select(RadPostAuth)
        if conditions:
            query = query.where(and_(*conditions))

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Items
        query = query.order_by(RadPostAuth.authdate.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_online_users(
        self, pagination: PaginationParams
    ) -> tuple[list[RadAcct], int]:
        query = select(RadAcct).where(RadAcct.acctstoptime.is_(None))

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Items
        query = query.order_by(RadAcct.acctstarttime.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def get_dashboard_stats(self) -> dict:
        # Total users
        from app.models.user import User
        from app.models.nas_client import NASClient
        from app.models.gateway import ReadonlyGateway

        users_result = await self.db.execute(select(func.count()).select_from(User))
        total_users = users_result.scalar() or 0

        # Online users
        online_result = await self.db.execute(
            select(func.count()).select_from(
                select(RadAcct).where(RadAcct.acctstoptime.is_(None)).subquery()
            )
        )
        online_users = online_result.scalar() or 0

        # NAS clients
        nas_result = await self.db.execute(select(func.count()).select_from(NASClient))
        total_nas = nas_result.scalar() or 0

        # Readonly gateways
        gw_result = await self.db.execute(select(func.count()).select_from(ReadonlyGateway))
        total_gateways = gw_result.scalar() or 0

        # Today's auth stats
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_auth = await self.db.execute(
            select(func.count()).select_from(
                select(RadPostAuth).where(RadPostAuth.authdate >= today_start).subquery()
            )
        )
        today_attempts = today_auth.scalar() or 0

        today_success = await self.db.execute(
            select(func.count()).select_from(
                select(RadPostAuth).where(
                    RadPostAuth.authdate >= today_start,
                    RadPostAuth.reply == "Access-Accept",
                ).subquery()
            )
        )
        today_ok = today_success.scalar() or 0

        return {
            "total_users": total_users,
            "active_users_online": online_users,
            "total_nas_clients": total_nas,
            "total_gateways": total_gateways,
            "today_auth_attempts": today_attempts,
            "today_auth_success": today_ok,
            "today_auth_failures": today_attempts - today_ok,
        }
