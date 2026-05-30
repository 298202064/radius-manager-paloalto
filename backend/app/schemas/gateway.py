from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.utils.network import validate_gateway_host


class GatewayCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    host: str = Field(..., max_length=255)
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: bool = True

    @model_validator(mode="after")
    def _validate_host(self):
        self.host = validate_gateway_host(self.host)
        return self


class GatewayUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    host: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=1, max_length=128)
    password: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    enabled: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_host(self):
        if self.host is not None:
            self.host = validate_gateway_host(self.host)
        return self


class GatewayResponse(BaseModel):
    id: int
    name: str
    host: str
    username: str
    description: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GatewayPage(BaseModel):
    items: list[GatewayResponse]
    total: int
    page: int
    page_size: int


class GatewayOnlineUser(BaseModel):
    username: str
    computer: Optional[str] = None
    client_os: Optional[str] = None
    virtual_ip: Optional[str] = None
    public_ip: Optional[str] = None
    login_time: Optional[str] = None
    tunnel_type: Optional[str] = None
    gateway_name: str = ""
    gateway_host: str = ""


class GatewayOnlineUserList(BaseModel):
    items: list[GatewayOnlineUser]
    total: int
