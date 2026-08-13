# Modem Data

Modem Data is a Home Assistant custom integration for retrieving diagnostic and
operational data from a supported cable modem. It polls the modem locally,
normalizes the response, and exposes the available values as Home Assistant
sensor entities.

The longer-term goal is to make modem events available to automations as well,
so users can trigger actions from events such as ranging failures, loss of
sync, registration changes, or other modem log entries. Event-log retrieval
and parsing are present in the client, but Home Assistant event/trigger
exposure is still planned work (see CC-004 in `TODO.md`).

## Current support

The integration currently supports:

- Arris TM3402A cable modems
- Status and hardware/firmware information
- Downstream and upstream channel information
- Interface, diplexer, and telephony information when provided by the modem
- Parsed DOCSIS and PacketCable event-log records for future event exposure
- HTTP and HTTPS connections
- Optional TLS certificate verification disablement for modems using a local
  or self-signed certificate

Additional modem models should not be advertised until their client, schema,
fixtures, and tests are complete.

## Installation

This is a custom integration. For a manual installation, copy the
`custom_components/modem_data` directory into the `custom_components`
directory of your Home Assistant configuration:

```text
<home-assistant-config>/custom_components/modem_data/
```

Restart Home Assistant after copying the files. If you use a custom-component
manager, install this repository according to that manager's instructions.

## Configuration

Add **Modem Data** from the Home Assistant integration setup screen. The setup
flow asks for:

1. The modem model.
2. The modem hostname or IP address.
3. The connection scheme: `http` or `https`.
4. The connection port.
5. Whether TLS certificate verification should be ignored.

The default connection for the Arris TM3402A is:

```text
https://192.168.100.1:443
```

The integration tests the connection and validates the modem response before
creating the config entry. Do not enable the TLS verification bypass unless
the modem is trusted through another means; disabling verification makes the
connection vulnerable to man-in-the-middle attacks.

After the first successful refresh, the resulting sensors are available under
the Modem Data device in **Settings → Devices & services** and can be added to
dashboards or used in automations.

## Sensors and updates

Sensors are generated from the selected modem model's normalized schema. This
keeps entity creation consistent as supported models are added. Scalar values
are exposed directly, while collection sensors report the number of records
and retain the records as state attributes.

The coordinator performs an initial refresh during setup and polls the modem
every 30 seconds. If the modem cannot be reached or returns an invalid payload,
the coordinator reports the update failure and the related entities may become
unavailable.

## Event triggers

The Arris client can retrieve and parse the modem's event-log page, including
DOCSIS and PacketCable records. A Home Assistant-facing event, trigger, service,
or diagnostics interface has not yet been selected or implemented. Until that
work is complete, event records are not exposed as automation triggers by the
integration.

## Troubleshooting

- Confirm that Home Assistant can reach the modem from the host running Home
  Assistant.
- Try the modem's web interface using the same scheme, host, and port.
- If HTTPS uses a self-signed certificate, enable the integration's TLS
  verification bypass only when appropriate for your local network.
- Check Home Assistant logs for connection or response-validation errors. The
  integration does not log modem credentials or raw modem pages.
- Make sure the selected model matches the actual modem. Model-specific
  parsers are intentionally not interchangeable.

## Development

The project uses Python 3.14.5, pytest, the Home Assistant custom-component
test harness, and Ruff. From the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff format --check .
python -m ruff check .
```

The repository also contains representative, anonymized Arris HTML responses
under `tests/resources/arris_tm3402a/`.

## Limitations and roadmap

The current roadmap includes:

- Exposing modem event logs through a stable Home Assistant interface
- Adding malformed-response, missing-value, placeholder-value, and schema
  failure parser tests
- Supporting additional modem models through dedicated clients and schemas
- Adding options/reconfiguration and diagnostics support

See `TODO.md` for the project task list.
