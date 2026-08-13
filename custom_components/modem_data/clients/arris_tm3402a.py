import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from .base import BaseModemClient
from .modem_client import ModemClient, parse_versions_page


def parse_number(value: str, as_int: bool = False) -> int | float | None:
    """Strip units and symbols to return a strict number or None."""
    if not value or value.strip() in ("-----", ""):
        return None
    cleaned = re.sub(r"[^\d.-]", "", value)
    if not cleaned:
        return None
    return int(float(cleaned)) if as_int else float(cleaned)


def parse_uptime_to_minutes(value: str) -> int | None:
    """Convert an Arris uptime string into total minutes."""
    if not value:
        return None
    match = re.search(r"(\d+)\s*d:\s*(\d+)\s*h:\s*(\d+)\s*m", value)
    if not match:
        return None
    days, hours, minutes = (int(part) for part in match.groups())
    return days * 1440 + hours * 60 + minutes


def parse_and_format_datetime(value: str) -> tuple[datetime | None, str]:
    """Parse an Arris event timestamp into a sortable datetime and ISO string."""
    try:
        parsed = datetime.strptime(value.strip(), "%m/%d/%Y %H:%M")
    except AttributeError, ValueError:
        return None, value
    return parsed, parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


class ArrisTM3402AClient(BaseModemClient):
    """Client and parser for the Arris TM3402A modem."""

    DEFAULT_SCHEME = "https"
    DEFAULT_HOST = "192.168.100.1"
    DEFAULT_PORT = 443

    def __init__(
        self,
        host: str,
        scheme: str = "https",
        port: int = 443,
        verify_ssl: bool = True,
    ) -> None:
        super().__init__(host)
        self._modem_client = ModemClient(
            host, scheme=scheme, port=port, verify_ssl=verify_ssl
        )
        self.schema = self._modem_client.schema

    def get_modem_status(self, html_content: str) -> dict[str, Any]:
        """Parse the Arris status page into the schema-defined payload."""
        soup = BeautifulSoup(html_content, "html.parser")
        payload: dict[str, Any] = {
            "status": {},
            "product_type": {"firmware": {}},
            "downstream_qam": [],
            "downstream_ofdm": [],
            "upstream_qam": [],
            "upstream_ofdm": [],
            "interfaces": [],
            "diplexer": [],
            "voip": [],
        }

        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            key = cells[0].get_text(strip=True).replace(":", "")
            value = cells[1].get_text(strip=True)
            status = payload["status"]
            product = payload["product_type"]
            if key == "System Uptime":
                status["system_uptime"] = parse_uptime_to_minutes(value)
            elif key == "Computers Detected":
                status["computers_detected"] = value
            elif key == "CM Status":
                status["cm_status"] = value
            elif key == "Time and Date":
                status["time_and_date"] = value
            elif key in {
                "Hardware Model",
                "Hardware Info",
                "Eth Sw Port 1",
                "Eth Sw Port 2",
                "Ethernet Phy Type",
                "Router",
                "Telemetry",
                "Line Card",
                "RF HW",
                "Market",
            }:
                product[key.lower().replace(" ", "_")] = value
            elif key == "Num Lines":
                product["num_lines"] = parse_number(value, True)

        def table_rows(title: str) -> list[list[Any]]:
            header = soup.find("h4", string=re.compile(title, re.I))
            table = header.find_next_sibling("table") if header else None
            return (
                [row.find_all("td") for row in table.find_all("tr") if row.find("td")]
                if table
                else []
            )

        for columns in table_rows("Downstream QAM"):
            if len(columns) == 9 and "Downstream" in columns[0].text:
                payload["downstream_qam"].append(
                    {
                        "channel": columns[0].get_text(strip=True),
                        "dcid": parse_number(columns[1].text, True),
                        "freq_mhz": parse_number(columns[2].text),
                        "power_dbmv": parse_number(columns[3].text),
                        "snr_db": parse_number(columns[4].text),
                        "modulation": columns[5].get_text(strip=True),
                        "octets": parse_number(columns[6].text, True),
                        "correcteds": parse_number(columns[7].text, True),
                        "uncorrectables": parse_number(columns[8].text, True),
                    }
                )

        for columns in table_rows("Downstream OFDM"):
            if len(columns) >= 9 and "Downstream" in columns[0].text:
                payload["downstream_ofdm"].append(
                    {
                        "channel": columns[0].get_text(strip=True),
                        "fft_type": columns[1].get_text(strip=True),
                        "channel_width_mhz": parse_number(columns[2].text, True),
                        "active_subcarriers": parse_number(columns[3].text, True),
                        "first_active_subcarrier_mhz": parse_number(
                            columns[4].text, True
                        ),
                        "last_active_subcarrier_mhz": parse_number(
                            columns[5].text, True
                        ),
                        "avg_rxmer_pilot_db": parse_number(columns[6].text),
                        "avg_rxmer_plc_db": parse_number(columns[7].text),
                        "avg_rxmer_data_db": parse_number(columns[8].text),
                    }
                )

        for columns in table_rows("Upstream QAM"):
            if len(columns) == 7 and "Upstream" in columns[0].text:
                payload["upstream_qam"].append(
                    {
                        "channel": columns[0].get_text(strip=True),
                        "ucid": parse_number(columns[1].text, True),
                        "freq_mhz": parse_number(columns[2].text),
                        "power_dbmv": parse_number(columns[3].text),
                        "channel_type": columns[4].get_text(strip=True),
                        "symbol_rate_ksym_s": parse_number(columns[5].text, True),
                        "modulation": columns[6].get_text(strip=True),
                    }
                )

        for columns in table_rows("Upstream OFDM"):
            if len(columns) == 9 and "Upstream" in columns[0].text:
                payload["upstream_ofdm"].append(
                    {
                        "channel": columns[0].get_text(strip=True),
                        "fft_type": columns[1].get_text(strip=True),
                        "channel_width_mhz": parse_number(columns[2].text, True),
                        "active_subcarriers": parse_number(columns[3].text, True),
                        "first_active_subcarrier_mhz": parse_number(
                            columns[4].text, True
                        ),
                        "last_active_subcarrier_mhz": parse_number(
                            columns[5].text, True
                        ),
                        "starting_freq_mhz": parse_number(columns[6].text),
                        "ending_freq_mhz": parse_number(columns[7].text),
                        "tx_power_dbmv": parse_number(columns[8].text),
                    }
                )

        self._parse_interfaces(soup, payload)
        self._parse_diplexer(soup, payload)
        self._parse_voip(soup, payload)
        return payload

    @staticmethod
    def _parse_interfaces(soup: BeautifulSoup, payload: dict[str, Any]) -> None:
        header = soup.find("div", string=re.compile("Interface Parameters", re.I))
        table = header.find_next_sibling("table") if header else None
        if not table:
            return
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) == 5:
                payload["interfaces"].append(
                    {
                        "interface_name": columns[0].get_text(strip=True),
                        "provisioned": columns[1].get_text(strip=True),
                        "state": columns[2].get_text(strip=True),
                        "speed_mbps": parse_number(columns[3].text, True),
                        "mac_address": columns[4].get_text(strip=True),
                    }
                )

    @staticmethod
    def _parse_diplexer(soup: BeautifulSoup, payload: dict[str, Any]) -> None:
        header = soup.find("div", string=re.compile("Diplexer", re.I))
        table = header.find_next_sibling("table") if header else None
        if not table:
            return
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) == 4:
                payload["diplexer"].append(
                    {
                        "band": columns[0].get_text(strip=True),
                        "upstream_range": columns[1].get_text(strip=True),
                        "downstream_range": columns[2].get_text(strip=True),
                        "current_band_setting": "X" in columns[3].get_text(strip=True),
                    }
                )

    @staticmethod
    def _parse_voip(soup: BeautifulSoup, payload: dict[str, Any]) -> None:
        table = soup.find("table", attrs={"cellpadding": "2", "border": "1"})
        if not table:
            return
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) == 9:
                payload["voip"].append(
                    {
                        "line": parse_number(columns[0].text, True),
                        "lc_state": columns[1].get_text(strip=True),
                        "callp_state": columns[2].get_text(strip=True),
                        "loop_current": columns[3].get_text(strip=True),
                        "hd_status": columns[4].get_text(strip=True),
                        "wb_slic": columns[5].get_text(strip=True),
                        "hd_enable": columns[6].get_text(strip=True),
                        "hd_endpnt_enable": columns[7].get_text(strip=True),
                        "hd_codec_provisioned": "Yes"
                        in columns[8].get_text(strip=True),
                    }
                )

    def get_modem_stats(self) -> dict:
        """Fetch, parse, and validate the Arris status payload."""
        status_html, versions_html = self._modem_client.get_status_pages()
        payload = self.get_modem_status(status_html)
        parse_versions_page(versions_html, payload)
        self._modem_client.validate_payload(payload)
        return payload

    def get_modem_logs(self) -> dict:
        """Fetch and parse the Arris event log."""
        return self.parse_modem_logs(self._modem_client.get_logs_page())

    @staticmethod
    def parse_modem_logs(html_content: str) -> dict[str, Any]:
        """Parse DOCSIS and MTA events from an Arris event page."""
        soup = BeautifulSoup(html_content, "html.parser")
        events: list[dict[str, Any]] = []

        docsis_table = soup.find("table", attrs={"cols": "4"})
        if docsis_table:
            for row in docsis_table.find_all("tr")[1:]:
                columns = row.find_all("td")
                if len(columns) != 4:
                    continue
                sort_date, date_time = parse_and_format_datetime(
                    columns[0].get_text(strip=True)
                )
                events.append(
                    {
                        "eventType": "DOCSIS",
                        "dateTime": date_time,
                        "eventId": int(columns[1].get_text(strip=True)),
                        "eventLevel": int(columns[2].get_text(strip=True)),
                        "description": columns[3].get_text(strip=True),
                        "_sort_date": sort_date,
                    }
                )

        mta_table = soup.find("table", attrs={"cols": "3"})
        if mta_table:
            for row in mta_table.find_all("tr")[1:]:
                columns = row.find_all("td")
                if len(columns) != 3:
                    continue
                sort_date, date_time = parse_and_format_datetime(
                    columns[0].get_text(strip=True)
                )
                events.append(
                    {
                        "eventType": "MTA",
                        "dateTime": date_time,
                        "eventId": int(columns[1].get_text(strip=True)),
                        "description": columns[2].get_text(strip=True),
                        "_sort_date": sort_date,
                    }
                )

        events.sort(key=lambda event: event["_sort_date"] or datetime.min, reverse=True)
        for event in events:
            del event["_sort_date"]
        return {"events": events}
