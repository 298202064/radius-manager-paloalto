from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.user import User
from app.models.radcheck import RadCheck
from app.models.otp_device import OTPDevice
from app.schemas.user import UserCreate, UserUpdate
from app.utils.pagination import PaginationParams


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(
        self, pagination: PaginationParams, search: str = "", enabled: bool | None = None
    ) -> tuple[list[User], int]:
        query = select(User)

        if search:
            query = query.where(
                or_(User.username.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"))
            )
        if enabled is not None:
            query = query.where(User.enabled == enabled)

        # Get total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get page
        query = query.order_by(User.id.desc())
        query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id).options(selectinload(User.otp_devices))
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_user(self, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            enabled=data.enabled,
            note=data.note,
        )
        self.db.add(user)
        await self.db.flush()  # Get user.id

        # Sync password to radcheck for RADIUS auth
        radcheck = RadCheck(
            username=data.username,
            attribute="Cleartext-Password",
            op=":=",
            value=data.password,
        )
        self.db.add(radcheck)

        await self.db.flush()
        return user

    async def update_user(self, user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            user.password_hash = hash_password(update_data["password"])
            # Update radcheck password
            result = await self.db.execute(
                select(RadCheck).where(
                    RadCheck.username == user.username,
                    RadCheck.attribute == "Cleartext-Password",
                )
            )
            rc = result.scalar_one_or_none()
            if rc:
                rc.value = update_data["password"]
            else:
                self.db.add(RadCheck(
                    username=user.username,
                    attribute="Cleartext-Password",
                    op=":=",
                    value=update_data["password"],
                ))
            del update_data["password"]

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        return user

    async def delete_user(self, user: User) -> None:
        # Clean up radcheck
        await self.db.execute(
            select(RadCheck).where(RadCheck.username == user.username)
        )
        await self.db.delete(user)

    async def has_otp_enabled(self, user_id: int) -> bool:
        result = await self.db.execute(
            select(OTPDevice).where(
                OTPDevice.user_id == user_id,
                OTPDevice.enabled == True,
            )
        )
        return result.scalar_one_or_none() is not None
