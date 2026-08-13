import json
import re
from datetime import datetime
from pathlib import Path

import requests
import urllib3
from bs4 import BeautifulSoup
from jsonschema import validate

from .base import host_for_url, normalize_host

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "tm3402a-schema.json"
with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
    MODEM_SCHEMA = json.load(schema_file)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_firmware_time(value: str) -> str:
    """Parse an Arris firmware date into an ISO 8601 string."""
    try:
        parsed = datetime.strptime(value, "%a %b %d %H:%M:%S %Z %Y")
    except TypeError, ValueError:
        return value
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_versions_page(html_content: str, payload: dict) -> None:
    """Extract firmware and hardware information into an existing payload."""
    soup = BeautifulSoup(html_content, "html.parser")
    product = payload["product_type"]
    firmware = product["firmware"]

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 2:
            continue
        key = cells[0].get_text(strip=True).replace(":", "")
        value = cells[1].get_text(strip=True)
        if key == "System":
            system_text = cells[1].get_text(separator="\n")
            for field in ("HW_REV", "VENDOR", "BOOTR", "SW_REV"):
                match = re.search(rf"{field}:\s*(.*)", system_text)
                if match:
                    product[field.lower()] = match.group(1).strip()
        elif key == "Serial Number":
            product["serial_number"] = value
        elif key == "Firmware Name":
            firmware["firmware_name"] = value
        elif key == "Firmware Build Time":
            firmware["firmware_build_time"] = parse_firmware_time(value)


class ModemClient:
    """Shared transport and schema-validation support for modem clients."""

    def __init__(
        self,
        host: str,
        scheme: str = "https",
        port: int = 443,
        verify_ssl: bool = True,
        schema: dict | None = None,
    ) -> None:
        self.host = normalize_host(host)
        self.scheme = scheme
        self.port = port
        self.verify_ssl = verify_ssl
        self.schema = schema or MODEM_SCHEMA

    def _base_url(self) -> str:
        return f"{self.scheme}://{host_for_url(self.host)}:{self.port}"

    def get_status_pages(self) -> tuple[str, str]:
        """Fetch the status and firmware pages for a model-specific parser."""
        base_url = self._base_url()
        status_response = requests.get(
            f"{base_url}/cgi-bin/status_cgi", timeout=10, verify=self.verify_ssl
        )
        status_response.raise_for_status()
        versions_response = requests.get(
            f"{base_url}/cgi-bin/vers_cgi", timeout=10, verify=self.verify_ssl
        )
        versions_response.raise_for_status()
        return status_response.text, versions_response.text

    def validate_payload(self, payload: dict) -> None:
        """Validate a model parser's normalized payload against its schema."""
        validate(instance=payload, schema=self.schema)

    def get_logs_page(self) -> str:
        """Fetch the raw modem event-log page for a model-specific parser."""
        response = requests.get(
            f"{self._base_url()}/cgi-bin/event_cgi",
            timeout=10,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.text
