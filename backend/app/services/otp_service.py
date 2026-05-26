import base64
import io
import pyotp
import qrcode

from app.models.otp_device import OTPDevice
from app.utils.encryption import encrypt_secret, decrypt_secret
from app.core.config import settings


class OTPService:
    @staticmethod
    def generate_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(secret: str, username: str, issuer: str = "RADIUS System") -> str:
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    @staticmethod
    def generate_qrcode_base64(uri: str) -> str:
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=2)

    @staticmethod
    def encrypt_otp_secret(secret: str) -> str:
        return encrypt_secret(secret)

    @staticmethod
    def decrypt_otp_secret(encrypted: str) -> str:
        return decrypt_secret(encrypted)

    @staticmethod
    def create_device_data(secret: str, username: str) -> dict:
        """Generate QR code data for OTP binding."""
        uri = OTPService.get_totp_uri(secret, username)
        qrcode_b64 = OTPService.generate_qrcode_base64(uri)
        return {
            "qrcode": qrcode_b64,
            "secret": secret,
            "uri": uri,
        }
