from pydantic import BaseModel, Field


class DynamicListUpdate(BaseModel):
    lines: list[str] = Field(default=[], max_length=5000)


class DynamicListResponse(BaseModel):
    lines: list[str]
    total: int
