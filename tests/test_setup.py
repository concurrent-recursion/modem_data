"""Tests for modem_data config-entry setup and unload lifecycle."""

from unittest.mock import patch

from custom_components.modem_data.const import (
    CONF_IGNORE_SSL,
    CONF_MODEL,
    CONF_SCHEME,
    DOMAIN,
)
from homeassistant.const import CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import MockConfigEntry

MODEL = "arris_tm3402a"


async def test_config_entry_setup_refresh_forward_and_unload(
    hass, enable_custom_integrations
):
    """Set up, refresh, forward, and unload a modem config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Modem (192.168.100.1)",
        unique_id="192.168.100.1",
        data={
            CONF_HOST: "192.168.100.1",
            CONF_MODEL: MODEL,
            CONF_SCHEME: "https",
            CONF_PORT: 443,
            CONF_IGNORE_SSL: False,
        },
    )
    entry.add_to_hass(hass)
    payload = {"status": {"system_uptime": 60, "cm_status": "Operational"}}

    with patch(
        "custom_components.modem_data.clients.arris_tm3402a.ArrisTM3402AClient.get_modem_stats",
        return_value=payload,
    ) as get_modem_stats:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    get_modem_stats.assert_called_once_with()
    coordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator.data == payload
    assert hass.states.async_entity_ids("sensor")

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
