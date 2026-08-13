"""Tests for the modem_data configuration flow."""

from unittest.mock import patch

import pytest
import requests
from custom_components.modem_data.clients.arris_tm3402a import (
    ArrisTM3402AClient,
)
from custom_components.modem_data.config_flow import ConfigFlow
from custom_components.modem_data.const import (
    CONF_IGNORE_SSL,
    CONF_MODEL,
    CONF_SCHEME,
    DOMAIN,
)
from homeassistant import data_entry_flow
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from jsonschema.exceptions import ValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

MODEL = "arris_tm3402a"


def create_flow(hass) -> ConfigFlow:
    """Create a flow with the state normally assigned by FlowManager."""
    flow = ConfigFlow()
    flow.hass = hass
    flow.handler = DOMAIN
    flow.flow_id = "test-flow"
    flow.context = {"source": SOURCE_USER}
    return flow


async def select_model(flow: ConfigFlow) -> dict:
    """Advance a flow to the connection step."""
    result = await flow.async_step_user({CONF_MODEL: MODEL})
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "connection"
    return result


def connection_input(**overrides) -> dict:
    """Return valid connection-form input."""
    values = {
        CONF_HOST: "192.168.100.1",
        CONF_SCHEME: "https",
        CONF_PORT: 443,
        CONF_IGNORE_SSL: False,
    }
    values.update(overrides)
    return values


async def test_model_step_shows_model_specific_defaults(hass):
    """The connection form is populated from the selected client defaults."""
    flow = create_flow(hass)

    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await select_model(flow)
    values = result["data_schema"]({})
    assert values[CONF_HOST] == "192.168.100.1"
    assert values[CONF_SCHEME] == "https"
    assert values[CONF_PORT] == 443
    assert values[CONF_IGNORE_SSL] is False


async def test_connection_creates_entry_with_overrides(hass):
    """A reachable modem creates an entry with overridden connection settings."""
    flow = create_flow(hass)
    await select_model(flow)

    with patch.object(ArrisTM3402AClient, "get_modem_stats", return_value={}):
        result = await flow.async_step_connection(
            connection_input(
                **{
                    CONF_HOST: "  MODEM.EXAMPLE. ",
                    CONF_SCHEME: "http",
                    CONF_PORT: 8080,
                    CONF_IGNORE_SSL: True,
                }
            )
        )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MODEL] == MODEL
    assert result["data"][CONF_HOST] == "modem.example"
    assert result["data"][CONF_SCHEME] == "http"
    assert result["data"][CONF_PORT] == 8080
    assert result["data"][CONF_IGNORE_SSL] is True
    assert result["title"] == "Modem (modem.example)"
    assert flow.unique_id == "modem.example"


async def test_connection_failure_returns_cannot_connect(hass):
    """Request failures are shown as a meaningful config-flow error."""
    flow = create_flow(hass)
    await select_model(flow)

    with patch.object(
        ArrisTM3402AClient,
        "get_modem_stats",
        side_effect=requests.exceptions.ConnectionError,
    ):
        result = await flow.async_step_connection(connection_input())

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_invalid_modem_response_returns_invalid_response(hass):
    """Schema/parser failures are reported separately from connectivity errors."""
    flow = create_flow(hass)
    await select_model(flow)

    with patch.object(
        ArrisTM3402AClient,
        "get_modem_stats",
        side_effect=ValidationError("payload does not match schema"),
    ):
        result = await flow.async_step_connection(connection_input())

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_response"}


async def test_duplicate_host_aborts(hass):
    """A host already configured in the integration cannot be added again."""
    existing = MockConfigEntry(
        domain=DOMAIN,
        unique_id="192.168.100.1",
        title="Existing modem",
        data={CONF_HOST: "192.168.100.1", CONF_MODEL: MODEL},
    )
    existing.add_to_hass(hass)

    flow = create_flow(hass)
    await select_model(flow)

    with pytest.raises(data_entry_flow.AbortFlow) as caught:
        await flow.async_step_connection(connection_input())

    assert caught.value.reason == "already_configured"
