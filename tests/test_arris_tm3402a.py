"""Fixture-based tests for the Arris TM3402A endpoints."""

from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import urlsplit

import pytest
from custom_components.modem_data.clients.arris_tm3402a import ArrisTM3402AClient

FIXTURE_DIR = Path(__file__).parent / "resources" / "arris_tm3402a"


def read_fixture(name: str) -> str:
    """Read a representative modem endpoint response."""
    return (FIXTURE_DIR / name).read_text(encoding="cp1252")


def response_for(text: str):
    """Return a response-shaped mock for the modem transport."""
    return Mock(text=text)


@pytest.fixture
def client() -> ArrisTM3402AClient:
    """Return an Arris client pointed at the documentation host."""
    return ArrisTM3402AClient("modem.example")


def test_get_modem_stats_parses_status_and_versions_fixtures(client):
    """The status and firmware endpoints produce a validated payload."""
    responses = {
        "/cgi-bin/status_cgi": response_for(read_fixture("status_cgi.htm")),
        "/cgi-bin/vers_cgi": response_for(read_fixture("vers_cgi.htm")),
    }

    def get_response(url: str, **kwargs):
        return responses[urlsplit(url).path]

    with patch(
        "custom_components.modem_data.clients.modem_client.requests.get",
        side_effect=get_response,
    ) as requests_get:
        stats = client.get_modem_stats()

    assert [call.args[0] for call in requests_get.call_args_list] == [
        "https://modem.example:443/cgi-bin/status_cgi",
        "https://modem.example:443/cgi-bin/vers_cgi",
    ]
    assert stats["status"]["system_uptime"] == 758
    assert stats["status"]["cm_status"] == "Telephony-Reg Complete"
    assert stats["product_type"]["serial_number"] == "SERIAL-00000001"
    assert stats["product_type"]["firmware"] == {
        "firmware_name": "TS11.05.048.01_061324_735.NCS.03",
        "firmware_build_time": "2024-06-13T09:29:42Z",
    }
    assert stats["downstream_qam"]
    assert stats["interfaces"][1]["speed_mbps"] is None


def test_get_modem_logs_parses_event_fixture(client):
    """The event endpoint produces sorted DOCSIS and MTA log records."""
    with patch(
        "custom_components.modem_data.clients.modem_client.requests.get",
        return_value=response_for(read_fixture("event_cgi.htm")),
    ) as requests_get:
        logs = client.get_modem_logs()

    requests_get.assert_called_once_with(
        "https://modem.example:443/cgi-bin/event_cgi",
        timeout=10,
        verify=True,
    )
    events = logs["events"]
    assert events
    assert {event["eventType"] for event in events} == {"DOCSIS", "MTA"}
    assert all("_sort_date" not in event for event in events)
    assert events[0]["dateTime"] == "2026-08-12T18:38:00Z"
    assert events[0]["eventId"] == 74010100
