import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .clients.base import BaseModemClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ModemDataCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching data from the cable modem."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: BaseModemClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=30),  # Polling interval
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch and transform data from the modem."""
        try:
            # Execute your extraction code (use hass.async_add_executor_job if non-async)
            return await self.hass.async_add_executor_job(self.client.get_modem_stats)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with modem: {err}") from err
