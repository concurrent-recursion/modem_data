# Agent Instructions

## Project overview

This repository is a Home Assistant custom integration for retrieving cable-modem status and event-log data. The integration is designed to support multiple modem models selected through the `model` config-flow field.

## Repository layout

- `custom_components/modem_data/__init__.py` — creates the model-specific client, starts the data coordinator, and forwards the sensor platform.
- `custom_components/modem_data/config_flow.py` — collects the modem host and model.
- `custom_components/modem_data/const.py` — integration domain, config keys, and supported model labels.
- `custom_components/modem_data/coordinator.py` — polls the selected client every 30 seconds and exposes its normalized data to entities.
- `custom_components/modem_data/sensor.py` — defines Home Assistant sensors backed by coordinator data.
- `custom_components/modem_data/clients/base.py` — abstract client contract.
- `custom_components/modem_data/clients/__init__.py` — model-key-to-client registry and client factory.
- `custom_components/modem_data/clients/<model>.py` — modem-model-specific retrieval and parsing logic.
- `custom_components/modem_data/clients/modem_client.py` — shared modem transport, schema validation, firmware parsing, and raw event-page retrieval.
- `custom_components/modem_data/manifest.json`, `strings.json`, `translations/`, and `schemas/` — Home Assistant metadata, UI strings, and model schemas.
- `requirements*.txt` — project and development dependencies at the repository root.

## Development guidance

- Cross-reference every project modification against `TODO.md`. Identify any applicable `CC-*` task labels, update the implementation as needed, and check off (`[x]`) a task only when its acceptance work is complete and validated. Add a new uniquely labeled TODO item when the change reveals work that is not already tracked.
- Preserve Home Assistant's async model. Network or blocking parser work must run through `hass.async_add_executor_job`, as the coordinator currently does.
- Every model client must subclass `BaseModemClient`, accept `host` in its constructor, and implement `get_modem_stats() -> dict`.
- Add a new model in all relevant places: the `SUPPORTED_MODELS` mapping in `custom_components/modem_data/const.py`, the client registry in `custom_components/modem_data/clients/__init__.py`, a dedicated client implementation, and its schema under `custom_components/modem_data/schemas/`.
- Client implementations should return the same normalized dictionary shape. Keep modem HTML/API quirks inside the model client rather than in the coordinator or sensor entities.
- Keep entity keys stable once exposed. Add sensors only for values that are present in the normalized client payload, and use stable unique IDs.
- Do not log modem credentials, API keys, raw modem pages, or other sensitive configuration data.
- Use relative package imports for integration modules (for example, `from .clients...`), and keep Home Assistant integration metadata consistent with the actual package/domain name.
- Prefer small, focused changes. Do not introduce a web server or duplicate polling path into the custom component.

## Validation

Before handing off changes:

1. Run the applicable test suite with the project's configured Home Assistant environment.
2. Run Ruff (or the repository's configured formatter/linter) on changed Python files.
3. Verify config-flow model values, client-registry keys, and sensor payload keys agree.
4. If a model parser changes, add or update fixture-based tests for representative modem responses, including missing/placeholder values and malformed responses.

Configuration-flow coverage now lives under `tests/`. Avoid claiming parser, coordinator, entity, or full Home Assistant lifecycle behavior is covered until those test areas are added.

## Known starting-state issues

The repository currently implements and registers only the Arris TM3402A client. Add a client implementation, schema, and registry entry before advertising another model in `SUPPORTED_MODELS`. Treat model support as an explicit compatibility boundary rather than falling back to a generic parser.
