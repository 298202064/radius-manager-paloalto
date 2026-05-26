from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RadPostAuth(Base):
    __tablename__ = "radpostauth"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, default="", index=True)
    pass_: Mapped[str] = mapped_column("pass", String(64), nullable=True)
    reply: Mapped[str] = mapped_column(String(32), nullable=True)
    calledstationid: Mapped[str] = mapped_column(String(50), nullable=True)
    callingstationid: Mapped[str] = mapped_column(String(50), nullable=True)
    authdate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
