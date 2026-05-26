from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LDAPConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    host: str = Field(..., max_length=255)
    port: int = Field(default=389, ge=1, le=65535)
    base_dn: str = Field(..., max_length=512)
    bind_dn: str = Field(..., max_length=512)
    bind_password: str = Field(..., min_length=1, max_length=255)
    use_tls: bool = False
    description: Optional[str] = None
    enabled: bool = True


class LDAPConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    host: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    base_dn: Optional[str] = Field(None, max_length=512)
    bind_dn: Optional[str] = Field(None, max_length=512)
    bind_password: Optional[str] = Field(None, min_length=1, max_length=255)
    use_tls: Optional[bool] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class LDAPConfigResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    base_dn: str
    bind_dn: str
    use_tls: bool
    description: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LDAPConfigPage(BaseModel):
    items: list[LDAPConfigResponse]
    total: int
    page: int
    page_size: int


class LDAPSearchRequest(BaseModel):
    search_filter: str = Field(
        default="(&(objectClass=user)(objectCategory=person))",
        max_length=500,
    )
    search_base: Optional[str] = Field(None, max_length=512)


class LDAPUserItem(BaseModel):
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    dn: str


class LDAPSearchResponse(BaseModel):
    items: list[LDAPUserItem]
    total: int


class LDAPImportRequest(BaseModel):
    usernames: list[str] = Field(..., min_length=1, max_length=100)


class LDAPImportResult(BaseModel):
    imported: list[dict] = []
    skipped: list[str] = []
    total_imported: int = 0
    total_skipped: int = 0
