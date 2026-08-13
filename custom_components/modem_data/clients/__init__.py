# from .netgear_cm1000 import NetgearCM1000Client
from .arris_tm3402a import ArrisTM3402AClient
from .base import BaseModemClient

CLIENT_MAP: dict[str, type[BaseModemClient]] = {
    # "netgear_cm1000": NetgearCM1000Client,
    "arris_tm3402a": ArrisTM3402AClient,
}


def get_client_for_model(
    model_key: str,
    host: str,
    scheme: str = "https",
    port: int = 443,
    verify_ssl: bool = True,
) -> BaseModemClient:
    """Instantiate and return the appropriate modem client."""
    client_cls = CLIENT_MAP.get(model_key)
    if not client_cls:
        raise ValueError(f"Unsupported modem model: {model_key}")
    return client_cls(
        host=host,
        scheme=scheme,
        port=port,
        verify_ssl=verify_ssl,
    )


def get_client_defaults(model_key: str) -> dict[str, str | int]:
    """Return connection defaults for a supported modem model."""
    client_cls = CLIENT_MAP.get(model_key)
    if not client_cls:
        raise ValueError(f"Unsupported modem model: {model_key}")
    return client_cls.connection_defaults()
