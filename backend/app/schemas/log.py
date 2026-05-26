from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union
from pydantic import BaseModel, field_validator


class AuthLogEntry(BaseModel):
    id: int
    username: str
    pass_: Optional[str] = None
    reply: Optional[str] = None
    calledstationid: Optional[str] = None
    callingstationid: Optional[str] = None
    authdate: datetime

    model_config = {"from_attributes": True}


class AuthLogPage(BaseModel):
    items: list[AuthLogEntry]
    total: int
    page: int
    page_size: int


class OnlineUserEntry(BaseModel):
    radacctid: int
    username: Optional[str] = None
    nasipaddress: str
    nasporttype: Optional[str] = None
    acctstarttime: Optional[datetime] = None
    acctinputoctets: Optional[int] = None
    acctoutputoctets: Optional[int] = None
    calledstationid: Optional[str] = None
    callingstationid: Optional[str] = None
    acctsessionid: str

    model_config = {"from_attributes": True}

    @field_validator("nasipaddress", mode="before")
    @classmethod
    def coerce_ip(cls, v: Union[str, IPv4Address, IPv6Address]) -> str:
        return str(v)


class OnlineUserPage(BaseModel):
    items: list[OnlineUserEntry]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_users: int
    active_users_online: int
    total_nas_clients: int
    total_gateways: int = 0
    today_auth_attempts: int
    today_auth_success: int
    today_auth_failures: int
