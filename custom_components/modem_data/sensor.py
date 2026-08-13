from collections.abc import Iterator
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SUPPORTED_MODELS


def _schema_sensor_definitions(
    schema: dict[str, Any], path: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], dict[str, Any]]]:
    """Yield leaf and collection properties described by a JSON schema."""
    for key, definition in schema.get("properties", {}).items():
        property_path = (*path, key)
        property_type = definition.get("type")
        if property_type == "object":
            yield from _schema_sensor_definitions(definition, property_path)
        elif property_type == "array":
            yield property_path, definition
        else:
            yield property_path, definition


def _get_value(data: dict[str, Any] | None, path: tuple[str, ...]) -> Any:
    for key in path:
        if not isinstance(data, dict) or key not in data:
            return None
        data = data[key]
    return data


def _display_name(path: tuple[str, ...]) -> str:
    return " ".join(part.replace("_", " ").title() for part in path)


def _unit_for(path: tuple[str, ...]) -> str | None:
    units = {
        "system_uptime": "min",
        "freq_mhz": "MHz",
        "channel_width_mhz": "MHz",
        "first_active_subcarrier_mhz": "MHz",
        "last_active_subcarrier_mhz": "MHz",
        "starting_freq_mhz": "MHz",
        "ending_freq_mhz": "MHz",
        "power_dbmv": "dBmV",
        "snr_db": "dB",
        "avg_rxmer_pilot_db": "dB",
        "avg_rxmer_plc_db": "dB",
        "avg_rxmer_data_db": "dB",
        "tx_power_dbmv": "dBmV",
        "speed_mbps": "Mbit/s",
        "symbol_rate_ksym_s": "kSym/s",
    }
    return units.get(path[-1])


async def async_setup_entry(hass, entry, async_add_entities):
    """Create sensors from the selected modem client's JSON schema."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    definitions = _schema_sensor_definitions(coordinator.client.schema)
    async_add_entities(
        SchemaModemSensor(coordinator, path, definition)
        for path, definition in definitions
    )


class SchemaModemSensor(CoordinatorEntity, SensorEntity):
    """A sensor whose value and metadata are driven by the modem schema."""

    def __init__(
        self, coordinator, path: tuple[str, ...], definition: dict[str, Any]
    ) -> None:
        super().__init__(coordinator)
        self._path = path
        self._is_collection = definition.get("type") == "array"
        self._is_numeric = definition.get("type") in ("integer", "number")
        self._attr_has_entity_name = True
        self._attr_name = _display_name(path)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{'.'.join(path)}"
        self._attr_native_unit_of_measurement = _unit_for(path)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=coordinator.config_entry.title,
            manufacturer="Cable modem",
            model=SUPPORTED_MODELS.get(
                coordinator.config_entry.data.get("model"), "Unknown"
            ),
        )
        if self._is_collection or self._is_numeric:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        """Return a scalar value or the number of records in a collection."""
        value = _get_value(self.coordinator.data, self._path)
        if self._is_collection and isinstance(value, list):
            return len(value)
        if isinstance(value, bool):
            return "on" if value else "off"
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose collection records as attributes without making them sensor state."""
        if not self._is_collection:
            return None
        value = _get_value(self.coordinator.data, self._path)
        return {"records": value} if isinstance(value, list) else None
