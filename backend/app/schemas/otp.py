from pydantic import BaseModel, Field


class OTPBindRequest(BaseModel):
    token: str = Field(..., min_length=6, max_length=6)


class OTPStatusResponse(BaseModel):
    enabled: bool
    device_name: str = "default"
    has_device: bool


class OTPQRResponse(BaseModel):
    qrcode: str  # base64 encoded PNG
    secret: str
    uri: str


class RADIUSAuthRequest(BaseModel):
    username: str
    password: str


class RADIUSAuthResponse(BaseModel):
    result: str  # "accept" or "reject"
    message: str = ""
    attributes: dict = {}
