from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NASClient(Base):
    __tablename__ = "nas_clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shortname: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    ip_address = mapped_column(INET, nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    radsecret: Mapped[str] = mapped_column(String(255), nullable=True)
    nas_type: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<NASClient {self.shortname}>"
