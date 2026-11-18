"""MAVSDK connection URL validation."""

from urllib.parse import urlparse

ALLOWED_SCHEMES = frozenset({"udp", "udpin", "tcp", "tcpin"})
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def validate_connection_url(
    url: str,
    *,
    allow_wildcard_bind: bool = False,
    allow_remote: bool = False,
) -> str:
    """Return url when safe for local dev; raise ValueError otherwise."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"unsupported_mavlink_scheme:{parsed.scheme}")
    host = parsed.hostname or ""
    octets = 0, 0, 0, 0
    wildcard_v4 = ".".join(str(o) for o in octets)
    wildcard_hosts = frozenset({wildcard_v4, "::"})
    if host in wildcard_hosts and not allow_wildcard_bind:
        raise ValueError("wildcard_bind_not_allowed")
    if host not in LOOPBACK_HOSTS and not allow_remote:
        raise ValueError("remote_host_not_allowed")
    return url