from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator


class NASClientCreate(BaseModel):
    shortname: str = Field(..., min_length=1, max_length=64)
    ip_address: str = Field(..., max_length=45)
    secret: str = Field(..., min_length=6, max_length=255)
    nas_type: str = Field(default="other", max_length=32)
    description: Optional[str] = None
    enabled: bool = True


class NASClientUpdate(BaseModel):
    shortname: Optional[str] = Field(None, min_length=1, max_length=64)
    ip_address: Optional[str] = Field(None, max_length=45)
    secret: Optional[str] = Field(None, min_length=6, max_length=255)
    nas_type: Optional[str] = Field(None, max_length=32)
    description: Optional[str] = None
    enabled: Optional[bool] = None


class NASClientResponse(BaseModel):
    id: int
    shortname: str
    ip_address: str
    nas_type: str
    description: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: datetime
    has_secret: bool = False

    model_config = {"from_attributes": True}

    @field_validator("ip_address", mode="before")
    @classmethod
    def coerce_ip(cls, v: Union[str, IPv4Address, IPv6Address]) -> str:
        return str(v)


class NASClientPage(BaseModel):
    items: list[NASClientResponse]
    total: int
    page: int
    page_size: int
