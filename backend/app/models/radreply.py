from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RadReply(Base):
    __tablename__ = "radreply"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, default="", index=True)
    attribute: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    op: Mapped[str] = mapped_column(String(2), nullable=False, default="==")
    value: Mapped[str] = mapped_column(String(253), nullable=False, default="")

    def __repr__(self) -> str:
        return f"<RadReply {self.username}: {self.attribute}>"
