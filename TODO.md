# Modem Data Custom Component TODO

Tasks are labeled so they can be referenced in issues, commits, and reviews. Tier tags (`Bronze`, `Silver`, `Gold`, and `Platinum`) identify requirements explicitly tied to `levels.md`; `Feature`, `Architecture`, and `Maintenance` identify important work that is not assigned to a specific tier there. Priority reflects the impact on Home Assistant compatibility; urgency reflects how soon the task should be addressed.

## Critical / Immediate

- [x] **[CC-001] [Bronze]** Make the Home Assistant test suite runnable in CI on a supported operating system. The current Windows environment cannot import the test harness because Home Assistant requires Unix-only `fcntl` support.
- [x] **[CC-002] [Bronze]** Add an end-to-end config-entry setup test covering `async_setup_entry`, the first coordinator refresh, platform forwarding, and `async_unload_entry` cleanup.
- [ ] **[CC-003] [Bronze]** Add parser fixtures and tests for valid TM3402A status pages, malformed HTML, missing required values, placeholder values such as `-----`, and schema validation failures.
- [ ] **[CC-004] [Feature]** Decide how modem event logs are exposed to Home Assistant and implement that interface. `get_modem_logs()` currently parses logs but is not called by a platform, service, event entity, or diagnostics endpoint.
- [ ] **[CC-005] [Bronze]** Verify the component in a real Home Assistant installation using the `custom_components/modem_data` directory and confirm config flow, entity creation, reload, and removal behavior.

## High / Before Release

- [ ] **[CC-006] [Silver]** Add a config-entry migration for entries created before scheme, port, SSL-verification, and unique-ID fields were introduced.
- [ ] **[CC-007] [Gold]** Add an options or reconfigure flow so users can change host, scheme, port, model, and SSL verification without removing the integration.
- [ ] **[CC-008] [Silver]** Add connection tests for HTTP, HTTPS with certificate verification, HTTPS with verification disabled, custom ports, IPv4 addresses, hostnames, and bracketed/unbracketed IPv6 addresses.
- [ ] **[CC-009] [Silver]** Replace broad config-flow exception handling with logged, narrowly classified exceptions while ensuring credentials, raw modem pages, and sensitive request data are never logged.
- [ ] **[CC-010] [Silver]** Add retry/backoff and explicit timeout behavior for modem requests, and distinguish connection failures from unsupported responses and schema failures.
- [ ] **[CC-011] [Bronze][Gold]** Add Home Assistant entity tests for stable unique IDs, device registration, native values, units, state classes, missing values, boolean values, and collection attributes.
- [ ] **[CC-012] [Silver]** Review collection sensors and avoid storing unbounded channel/interface/log records in state attributes. Use dedicated entities, diagnostics, or a bounded representation where appropriate.
- [ ] **[CC-013] [Gold]** Add diagnostics support with redaction for useful troubleshooting data such as selected model, connection scheme/port, parser status, and sanitized modem metadata.

## Medium / Important Improvements

- [ ] **[CC-014] [Gold]** Add a schema-to-entity metadata contract for names, units, device classes, state classes, diagnostic categories, and whether a property should become a sensor, binary sensor, text sensor, or attribute.
- [ ] **[CC-015] [Architecture]** Move model-specific schema selection into the model client registry so each modem client loads and validates against its own schema.
- [ ] **[CC-016] [Bronze]** Add a complete client contract test suite for `BaseModemClient`, including default connection settings and unsupported-model behavior.
- [ ] **[CC-017] [Bronze]** Implement each advertised modem model or keep it hidden until its client, parser, schema, fixtures, and tests are complete.
- [ ] **[CC-018] [Gold]** Add a shared entity/device helper so all future platforms use the same device identifier, naming, model, manufacturer, and connection metadata.
- [ ] **[CC-019] [Gold]** Add localized translations for every supported language required by the project, or document that English is the initial supported translation.
- [ ] **[CC-020] [Maintenance]** Add Home Assistant version compatibility guidance and verify the integration against the minimum supported Home Assistant release.
- [ ] **[CC-021] [Bronze][Platinum]** Pin or constrain development tooling versions and document the supported Python, Home Assistant, pytest, and Ruff versions.
- [ ] **[CC-022] [Bronze][Gold]** Add a CI workflow that runs Ruff, formatting checks, JSON/schema validation, pytest, and any Home Assistant integration validation tools.

## Low / Quality and Maintenance

- [ ] **[CC-023] [Bronze][Silver][Gold]** Add README documentation covering installation, supported models, configuration fields, TLS behavior, exposed entities, troubleshooting, and limitations.
- [x] **[CC-024] [Bronze]** Add representative modem HTML fixtures to the repository without including credentials, public IPs, MAC addresses, serial numbers, or other identifying data.
- [ ] **[CC-025] [Bronze]** Add schema checks to CI and verify that parser output keys, sensor paths, required fields, and schema types remain synchronized.
- [ ] **[CC-026] [Maintenance]** Add a versioning and release checklist covering manifest version updates, migration versions, changelog entries, and backward compatibility.
- [ ] **[CC-027] [Maintenance]** Review dependency usage and remove any runtime dependency that Home Assistant already provides or that is not required by the custom component.
- [ ] **[CC-028] [Platinum]** Add type checking for integration modules and client payloads once the normalized payload types are formalized.
- [ ] **[CC-029] [Gold]** Add coverage reporting and establish minimum coverage targets for config flow, coordinator, clients, parsers, and entities.
- [ ] **[CC-030] [Maintenance]** Review Home Assistant quality-scale requirements periodically and update this checklist as the integration gains platforms or services.

## Existing coverage

The current configuration-flow tests in `tests/test_config_flow.py` cover model selection, model defaults, user overrides, host normalization, connectivity errors, invalid responses, and duplicate hosts. They should be extended as the related tasks above are completed.

## Bronze-tier cross-reference

The Bronze criteria from `levels.md` map to the existing tasks as follows:

| Bronze criterion | Existing coverage | Remaining gap |
|---|---|---|
| UI setup | `CC-005`, `CC-023` | The end-user setup instructions must explicitly walk through adding the integration from the Home Assistant UI. |
| Basic coding standards | Ruff configuration and checks; `CC-022` | No additional task required beyond keeping the checks passing. |
| Correctly configured automated tests | `CC-001`–`CC-003`, `CC-011`, `CC-022` | The suite still needs to run successfully in a supported CI environment. |
| Basic end-user documentation | `CC-023` | Documentation must include a complete beginner-friendly setup path, not only developer notes. |
| Quality-scale tracking | Not currently covered | Add and maintain the integration quality-scale checklist. |

### Additional Bronze tasks

- [ ] **[CC-031] [Bronze]** Create `custom_components/modem_data/quality_scale.yaml` documenting the Bronze rules, their completion status, and any justified exemptions.
- [ ] **[CC-032] [Bronze]** Add beginner-oriented documentation with a step-by-step Home Assistant UI setup guide, including installation location, model selection, connection fields, SSL behavior, the first connectivity check, and where the resulting entities appear.


## Reference Checklist

This is the reference checklist from Home Assistant's integration quality-scale documentation. 
DO NOT modify this checklist other than checking or unchecking tasks.

### Bronze
- [ ] `action-setup` - Service actions are registered in async_setup
- [ ] `appropriate-polling` - If it's a polling integration, set an appropriate polling interval
- [ ] `brands` - Has branding assets available for the integration
- [ ] `common-modules` - Place common patterns in common modules
- [ ] `config-flow-test-coverage` - Full test coverage for the config flow
- [ ] `config-flow` - Integration needs to be able to be set up via the UI
    - [ ] Uses `data_description` to give context to fields
    - [ ] Uses `ConfigEntry.data` and `ConfigEntry.options` correctly
- [ ] `dependency-transparency` - Dependency transparency
- [ ] `docs-actions` - The documentation describes the provided service actions that can be used
- [ ] `docs-triggers` - The documentation describes the provided triggers that can be used
- [ ] `docs-conditions` - The documentation describes the provided conditions that can be used
- [ ] `docs-high-level-description` - The documentation includes a high-level description of the integration brand, product, or service
- [ ] `docs-installation-instructions` - The documentation provides step-by-step installation instructions for the integration, including, if needed, prerequisites
- [ ] `docs-removal-instructions` - The documentation provides removal instructions
- [ ] `entity-event-setup` - Entity events are subscribed in the correct lifecycle methods
- [ ] `entity-unique-id` - Entities have a unique ID
- [ ] `has-entity-name` - Entities use has_entity_name = True
- [ ] `runtime-data` - Use ConfigEntry.runtime_data to store runtime data
- [ ] `test-before-configure` - Test a connection in the config flow
- [ ] `test-before-setup` - Check during integration initialization if we are able to set it up correctly
- [ ] `unique-config-entry` - Don't allow the same device or service to be able to be set up twice

### Silver
- [ ] `action-exceptions` - Service actions raise exceptions when encountering failures
- [ ] `config-entry-unloading` - Support config entry unloading
- [ ] `docs-configuration-parameters` - The documentation describes all integration configuration options
- [ ] `docs-installation-parameters` - The documentation describes all integration installation parameters
- [ ] `entity-unavailable` - Mark entity unavailable if appropriate
- [ ] `integration-owner` - Has an integration owner
- [ ] `log-when-unavailable` - If internet/device/service is unavailable, log once when unavailable and once when back connected
- [ ] `parallel-updates` - Number of parallel updates is specified
- [ ] `reauthentication-flow` - Reauthentication needs to be available via the UI
- [ ] `test-coverage` - Above 95% test coverage for all integration modules

### Gold
- [ ] `devices` - The integration creates devices
- [ ] `diagnostics` - Implements diagnostics
- [ ] `discovery-update-info` - Integration uses discovery info to update network information
- [ ] `discovery` - Devices can be discovered
- [ ] `docs-data-update` - The documentation describes how data is updated
- [ ] `docs-examples` - The documentation provides automation examples the user can use.
- [ ] `docs-known-limitations` - The documentation describes known limitations of the integration (not to be confused with bugs)
- [ ] `docs-supported-devices` - The documentation describes known supported / unsupported devices
- [ ] `docs-supported-functions` - The documentation describes the supported functionality, including entities, and platforms
- [ ] `docs-troubleshooting` - The documentation provides troubleshooting information
- [ ] `docs-use-cases` - The documentation describes use cases to illustrate how this integration can be used
- [ ] `dynamic-devices` - Devices added after integration setup
- [ ] `entity-category` - Entities are assigned an appropriate EntityCategory
- [ ] `entity-device-class` - Entities use device classes where possible
- [ ] `entity-disabled-by-default` - Integration disables less popular (or noisy) entities
- [ ] `entity-translations` - Entities have translated names
- [ ] `exception-translations` - Exception messages are translatable
- [ ] `icon-translations` - Entities implement icon translations
- [ ] `reconfiguration-flow` - Integrations should have a reconfigure flow
- [ ] `repair-issues` - Repair issues and repair flows are used when user intervention is needed
- [ ] `stale-devices` - Stale devices are removed

### Platinum
- [ ] `async-dependency` - Dependency is async
- [ ] `inject-websession` - The integration dependency supports passing in a websession
- [ ] `strict-typing` - Strict typing