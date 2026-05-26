from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RadAcct(Base):
    __tablename__ = "radacct"

    radacctid: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    acctsessionid: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    acctuniqueid: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    username: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    groupname: Mapped[str] = mapped_column(String(64), nullable=True)
    realm: Mapped[str] = mapped_column(String(64), nullable=True)
    nasipaddress = mapped_column(INET, nullable=False, default="0.0.0.0")
    nasportid: Mapped[str] = mapped_column(String(15), nullable=True)
    nasporttype: Mapped[str] = mapped_column(String(32), nullable=True)
    acctstarttime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    acctupdatetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    acctstoptime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    acctinterval: Mapped[int] = mapped_column(Integer, nullable=True)
    acctinputoctets: Mapped[int] = mapped_column(BigInteger, nullable=True)
    acctoutputoctets: Mapped[int] = mapped_column(BigInteger, nullable=True)
    acctinputgigawords: Mapped[int] = mapped_column(BigInteger, nullable=True)
    acctoutputgigawords: Mapped[int] = mapped_column(BigInteger, nullable=True)
    accttotalgigawords: Mapped[int] = mapped_column(BigInteger, nullable=True)
    calledstationid: Mapped[str] = mapped_column(String(50), nullable=True)
    callingstationid: Mapped[str] = mapped_column(String(50), nullable=True)
    connectinfo_start: Mapped[str] = mapped_column(String(50), nullable=True)
    connectinfo_stop: Mapped[str] = mapped_column(String(50), nullable=True)
    acctterminatecause: Mapped[str] = mapped_column(String(32), nullable=True)
    servicetype: Mapped[str] = mapped_column(String(32), nullable=True)
    framedprotocol: Mapped[str] = mapped_column(String(32), nullable=True)
    framedipaddress = mapped_column(INET, nullable=True)
