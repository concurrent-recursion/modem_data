import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from jsonschema.exceptions import ValidationError

from .clients import get_client_defaults, get_client_for_model
from .clients.base import normalize_host
from .const import (
    CONF_IGNORE_SSL,
    CONF_MODEL,
    CONF_SCHEME,
    DOMAIN,
    SUPPORTED_MODELS,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cable Modem."""

    VERSION = 1

    def __init__(self) -> None:
        self._model_key: str | None = None

    async def async_step_user(self, user_input=None):
        """Select the modem model."""
        if user_input is not None:
            self._model_key = user_input[CONF_MODEL]
            return await self.async_step_connection()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_MODEL): vol.In(SUPPORTED_MODELS)}
            ),
        )

    async def async_step_connection(self, user_input=None):
        """Configure connection settings using model-specific defaults."""
        defaults = get_client_defaults(self._model_key)

        if user_input is not None:
            try:
                host = normalize_host(user_input[CONF_HOST])
            except ValueError:
                return self.async_show_form(
                    step_id="connection",
                    data_schema=self._connection_schema(defaults),
                    errors={"base": "invalid_host"},
                )
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            errors = {}
            client = get_client_for_model(
                self._model_key,
                host=host,
                scheme=user_input[CONF_SCHEME],
                port=user_input[CONF_PORT],
                verify_ssl=not user_input[CONF_IGNORE_SSL],
            )
            try:
                await self.hass.async_add_executor_job(client.get_modem_stats)
            except requests.exceptions.RequestException:
                errors["base"] = "cannot_connect"
            except ValidationError:
                errors["base"] = "invalid_response"
            except ValueError, TypeError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"

            if errors:
                return self.async_show_form(
                    step_id="connection",
                    data_schema=self._connection_schema(defaults),
                    errors=errors,
                )

            data = {CONF_MODEL: self._model_key, **user_input, CONF_HOST: host}
            return self.async_create_entry(title=f"Modem ({host})", data=data)

        return self.async_show_form(
            step_id="connection",
            data_schema=self._connection_schema(defaults),
        )

    @staticmethod
    def _connection_schema(defaults: dict[str, str | int]) -> vol.Schema:
        """Build the connection form schema from model defaults."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=defaults[CONF_HOST]): vol.All(
                    str, vol.Length(min=1)
                ),
                vol.Required(CONF_SCHEME, default=defaults[CONF_SCHEME]): vol.In(
                    ("http", "https")
                ),
                vol.Required(CONF_PORT, default=defaults[CONF_PORT]): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_IGNORE_SSL, default=False): vol.Coerce(bool),
            }
        )
