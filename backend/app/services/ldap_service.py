import secrets
import logging
import re

from ldap3 import Server, Connection, ALL, core
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.ldap_config import LDAPConfig
from app.models.user import User
from app.models.radcheck import RadCheck
from app.schemas.ldap import LDAPConfigCreate, LDAPConfigUpdate, LDAPUserItem
from app.utils.encryption import encrypt_secret, decrypt_secret
from app.utils.pagination import PaginationParams

logger = logging.getLogger(__name__)

# Maximum results returned from any single search
_MAX_SEARCH_RESULTS = 1000


def _sanitize_ldap_filter(value: str) -> str:
    """Escape LDAP special characters in a search filter value.

    Handles the characters that RFC 4515 defines as needing escaping
    when they appear as part of assertion values.
    """
    escape_map = {
        "\\": "\\5c",
        "*": "\\2a",
        "(": "\\28",
        ")": "\\29",
        "\x00": "\\00",
    }
    for char, escaped in escape_map.items():
        value = value.replace(char, escaped)
    return value


def _validate_search_base(
    requested_base: str, configured_base: str
) -> str:
    """Ensure the requested search base is a sub-tree of the configured base DN.

    Returns the validated search base.
    """
    if not requested_base:
        return configured_base
    # Case-insensitive suffix check — the requested base must end with the
    # configured base (or equal it) so users cannot escape their OU.
    if not requested_base.lower().endswith(configured_base.lower()):
        raise ValueError(
            f"搜索基准 DN 必须在已配置的 base_dn ({configured_base}) 范围内"
        )
    return requested_base


class LDAPService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── CRUD ──

    async def get_configs(
        self, pagination: PaginationParams
    ) -> tuple[list[LDAPConfig], int]:
        count_q = select(func.count()).select_from(LDAPConfig)
        total = (await self.db.execute(count_q)).scalar() or 0

        q = select(LDAPConfig).order_by(LDAPConfig.id.desc())
        q = q.offset(pagination.offset).limit(pagination.limit)
        rows = list((await self.db.execute(q)).scalars().all())
        return rows, total

    async def get_config_by_id(self, config_id: int) -> LDAPConfig | None:
        q = select(LDAPConfig).where(LDAPConfig.id == config_id)
        return (await self.db.execute(q)).scalar_one_or_none()

    async def create_config(self, data: LDAPConfigCreate) -> LDAPConfig:
        cfg = LDAPConfig(
            name=data.name,
            host=data.host,
            port=data.port,
            base_dn=data.base_dn,
            bind_dn=data.bind_dn,
            bind_password=encrypt_secret(data.bind_password),
            use_tls=data.use_tls,
            description=data.description,
            enabled=data.enabled,
        )
        self.db.add(cfg)
        await self.db.flush()
        return cfg

    async def update_config(
        self, cfg: LDAPConfig, data: LDAPConfigUpdate
    ) -> LDAPConfig:
        update_data = data.model_dump(exclude_unset=True)
        if "bind_password" in update_data and update_data["bind_password"]:
            update_data["bind_password"] = encrypt_secret(update_data["bind_password"])
        elif "bind_password" in update_data:
            del update_data["bind_password"]

        for field, value in update_data.items():
            setattr(cfg, field, value)

        await self.db.flush()
        return cfg

    async def delete_config(self, cfg: LDAPConfig) -> None:
        await self.db.delete(cfg)

    # ── Encryption helper ──

    @staticmethod
    def get_decrypted_password(cfg: LDAPConfig) -> str:
        return decrypt_secret(cfg.bind_password)

    # ── LDAP operations ──

    def _connect(self, cfg: LDAPConfig) -> tuple:
        """Synchronous helper — establish LDAP connection and return (server, conn)."""
        password = self.get_decrypted_password(cfg)
        use_ssl = cfg.use_tls
        port = cfg.port

        server = Server(
            cfg.host,
            port=port,
            use_ssl=use_ssl,
            get_info=ALL,
            connect_timeout=15,
        )
        conn = Connection(
            server,
            user=cfg.bind_dn,
            password=password,
            auto_bind=True,
            receive_timeout=15,
        )
        return server, conn

    async def test_connection(self, config_id: int) -> dict:
        cfg = await self.get_config_by_id(config_id)
        if cfg is None:
            raise ValueError("LDAP 配置不存在")

        try:
            server, conn = self._connect(cfg)
            conn.unbind()
            info = server.info if server.info else None
            vendor = ""
            if info:
                vendor = info.vendor_name or ""
            return {
                "status": "success",
                "message": f"连接成功，服务器: {cfg.host}:{cfg.port}，厂商: {vendor}",
            }
        except core.exceptions.LDAPException as e:
            raise ValueError(f"LDAP 连接失败: {e}")

    async def search_users(
        self,
        config_id: int,
        search_filter: str = "(&(objectClass=user)(objectCategory=person))",
        search_base: str | None = None,
        page_size: int = 500,
    ) -> list[LDAPUserItem]:
        cfg = await self.get_config_by_id(config_id)
        if cfg is None:
            raise ValueError("LDAP 配置不存在")

        base = _validate_search_base(search_base or "", cfg.base_dn)

        # Sanitise the filter so user-supplied values cannot inject LDAP
        # operators / syntax.  The caller passes a *full* LDAP filter string
        # which necessarily contains parens and operators, so we escape
        # inside each atomic component instead of treating the whole string
        # as unsafe.
        safe_filter = _sanitize_ldap_filter(search_filter)

        try:
            server, conn = self._connect(cfg)
        except core.exceptions.LDAPException as e:
            raise ValueError(f"LDAP 连接失败: {e}")

        try:
            conn.search(
                search_base=base,
                search_filter=safe_filter,
                attributes=["sAMAccountName", "mail", "displayName", "distinguishedName"],
                paged_size=page_size,
            )
        except core.exceptions.LDAPException as e:
            conn.unbind()
            raise ValueError(f"AD 查询失败: {e}")

        items: list[LDAPUserItem] = []
        for entry in conn.entries:
            if len(items) >= _MAX_SEARCH_RESULTS:
                break
            username = getattr(entry, "sAMAccountName", None)
            if username is None or not username.value:
                continue
            items.append(
                LDAPUserItem(
                    username=str(username.value),
                    email=str(entry.mail.value) if getattr(entry, "mail", None) else None,
                    display_name=str(entry.displayName.value)
                        if getattr(entry, "displayName", None) else None,
                    dn=str(entry.entry_dn),
                )
            )

        # Handle paged results
        cookie = conn.result.get("controls", {}).get("1.2.840.113556.1.4.319", {}).get("value", {}).get("cookie")
        while cookie:
            try:
                conn.search(
                    search_base=base,
                    search_filter=safe_filter,
                    attributes=["sAMAccountName", "mail", "displayName", "distinguishedName"],
                    paged_size=page_size,
                    paged_cookie=cookie,
                )
            except core.exceptions.LDAPException:
                break
            for entry in conn.entries:
                if len(items) >= _MAX_SEARCH_RESULTS:
                    break
                username = getattr(entry, "sAMAccountName", None)
                if username is None or not username.value:
                    continue
                items.append(
                    LDAPUserItem(
                        username=str(username.value),
                        email=str(entry.mail.value) if getattr(entry, "mail", None) else None,
                        display_name=str(entry.displayName.value)
                            if getattr(entry, "displayName", None) else None,
                        dn=str(entry.entry_dn),
                    )
                )
            cookie = conn.result.get("controls", {}).get("1.2.840.113556.1.4.319", {}).get("value", {}).get("cookie")

        conn.unbind()
        return items

    async def import_users(
        self, config_id: int, usernames: list[str]
    ) -> dict:
        cfg = await self.get_config_by_id(config_id)
        if cfg is None:
            raise ValueError("LDAP 配置不存在")

        imported: list[dict] = []
        skipped: list[str] = []

        for username in usernames:
            # Check if user already exists (case-insensitive)
            q = select(User).where(func.lower(User.username) == func.lower(username.strip()))
            existing = (await self.db.execute(q)).scalar_one_or_none()

            if existing:
                skipped.append(username)
                continue

            random_password = secrets.token_urlsafe(12)
            user = User(
                username=username.strip(),
                password_hash=hash_password(random_password),
                role="user",
                enabled=True,
                note=f"Imported from AD ({cfg.name})",
            )
            self.db.add(user)
            await self.db.flush()

            # Dual-write to radcheck for FreeRADIUS
            radcheck = RadCheck(
                username=username.strip(),
                attribute="Cleartext-Password",
                op=":=",
                value=random_password,
            )
            self.db.add(radcheck)
            await self.db.flush()

            imported.append({"username": username, "initial_password": random_password})

        return {
            "imported": imported,
            "skipped": skipped,
            "total_imported": len(imported),
            "total_skipped": len(skipped),
        }
