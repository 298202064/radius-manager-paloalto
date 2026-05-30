import ipaddress
import re
import logging

logger = logging.getLogger(__name__)

# Hostname regex per RFC 1123
_HOSTNAME_RE = re.compile(
    r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
)

# Networks that should never be accessed from the backend
_BLOCKED_NETS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local (includes cloud metadata)
    ipaddress.ip_network("::1/128"),            # IPv6 loopback
]

# Specific metadata endpoints (defense-in-depth, covered by 169.254.0.0/16 above)
_METADATA_IPS = frozenset([
    ipaddress.ip_address("169.254.169.254"),    # AWS / GCP / Azure
    ipaddress.ip_address("100.100.100.200"),    # Alibaba Cloud
])


def validate_gateway_host(host: str) -> str:
    """Validate a gateway host address to prevent SSRF.

    Blocks loopback, link-local, cloud metadata endpoints,
    and malformed addresses.  Private RFC 1918 addresses are
        allowed since gateways commonly live on internal networks.

    Returns the trimmed host on success.
    Raises ValueError with a Chinese-language message on failure.
    """
    if not host or not host.strip():
        raise ValueError("主机地址不能为空")

    host = host.strip()

    # Block URL scheme injection
    if "://" in host:
        raise ValueError("主机地址不能包含 URL 协议前缀")

    # Block path / port / userinfo injection
    if "/" in host or "\\" in host:
        raise ValueError("主机地址不能包含路径分隔符")
    if "@" in host:
        raise ValueError("主机地址不能包含 '@' 符号")

    # Reject trailing dot (fully-qualified confusion)
    host = host.rstrip(".")

    # Try as IP address — check validity first to avoid catching our own errors
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        pass  # Not an IP, continue to hostname check below
    else:
        for net in _BLOCKED_NETS:
            if addr in net:
                raise ValueError(f"不允许访问内部或链路本地地址: {host}")
        if addr in _METADATA_IPS:
            raise ValueError(f"不允许访问云元数据服务地址: {host}")
        return host

    # Hostname validation
    if len(host) > 253:
        raise ValueError("主机地址过长")
    if not _HOSTNAME_RE.match(host):
        raise ValueError("主机地址格式无效")

    # Block common local hostnames
    if host.lower() in ("localhost", "localhost.localdomain", "local", "broadcasthost"):
        raise ValueError("不允许访问本地主机")

    return host
