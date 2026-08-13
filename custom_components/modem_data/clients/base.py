import ipaddress
from abc import ABC, abstractmethod


def normalize_host(value: str) -> str:
    """Normalize an IPv4 address, IPv6 address, or hostname."""
    host = value.strip()
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    if not host:
        raise ValueError("Host must not be empty")

    try:
        return ipaddress.ip_address(host).compressed
    except ValueError:
        return host.rstrip(".").lower()


def host_for_url(host: str) -> str:
    """Return a normalized host formatted for use in a URL authority."""
    normalized = normalize_host(host)
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        return normalized
    return f"[{normalized}]" if address.version == 6 else normalized


class BaseModemClient(ABC):
    """Base class for all modem clients."""

    DEFAULT_SCHEME = "https"
    DEFAULT_HOST = "192.168.100.1"
    DEFAULT_PORT = 443

    def __init__(self, host: str) -> None:
        self.host = host

    @classmethod
    def connection_defaults(cls) -> dict[str, str | int]:
        """Return the model's default connection settings."""
        return {
            "scheme": cls.DEFAULT_SCHEME,
            "host": cls.DEFAULT_HOST,
            "port": cls.DEFAULT_PORT,
        }

    @abstractmethod
    def get_modem_stats(self) -> dict:
        """Fetch and parse data into a standardized dictionary."""
        pass

    def get_modem_logs(self) -> dict:
        """Fetch and parse the modem event log, when supported."""
        raise NotImplementedError
