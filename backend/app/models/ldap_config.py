from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LDAPConfig(Base):
    __tablename__ = "ldap_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=389)
    base_dn: Mapped[str] = mapped_column(String(512), nullable=False)
    bind_dn: Mapped[str] = mapped_column(String(512), nullable=False)
    bind_password: Mapped[str] = mapped_column(String(512), nullable=False)
    use_tls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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
        return f"<LDAPConfig {self.name}>"
