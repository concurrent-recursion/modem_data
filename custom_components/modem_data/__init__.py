from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .clients import get_client_defaults, get_client_for_model
from .clients.base import normalize_host
from .const import CONF_IGNORE_SSL, CONF_MODEL, CONF_SCHEME, DOMAIN
from .coordinator import ModemDataCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cable Modem from a config entry."""
    model_key = entry.data[CONF_MODEL]
    defaults = get_client_defaults(model_key)
    host = normalize_host(entry.data.get(CONF_HOST, defaults[CONF_HOST]))
    scheme = entry.data.get(CONF_SCHEME, defaults[CONF_SCHEME])
    port = entry.data.get(CONF_PORT, defaults[CONF_PORT])
    ignore_ssl = entry.data.get(CONF_IGNORE_SSL, False)

    # Dynamically select and instantiate client based on selected model
    client = get_client_for_model(
        model_key,
        host=host,
        scheme=scheme,
        port=port,
        verify_ssl=not ignore_ssl,
    )

    # Pass the config entry into the coordinator so entities and lifecycle
    # management can use the entry associated with this modem.
    coordinator = ModemDataCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a modem config entry and release its coordinator."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    entries = hass.data.get(DOMAIN)
    if entries is not None:
        entries.pop(entry.entry_id, None)
        if not entries:
            hass.data.pop(DOMAIN, None)

    return True
