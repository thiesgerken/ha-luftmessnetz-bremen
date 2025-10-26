"""Coordinator for the Luftmessnetz Bremen integration."""

from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CSV_URL, DEFAULT_STATION, DEFAULT_UPDATE_INTERVAL, DOMAIN, LOGGER


class LuftmessnetzClient:
    """Async HTTP client for Luftmessnetz Bremen CSV data."""

    def __init__(self, session: ClientSession, station: str = DEFAULT_STATION) -> None:
        """Initialize the client with a shared session and station id."""
        self._session = session
        self._station = station

    def _build_url(self) -> str:
        now = datetime.now()
        start = now - timedelta(days=1)
        params = (
            f"?group=pollution&period=1h&timespan=custom"
            f"&start%5Bdate%5D={start.strftime('%d.%m.%Y')}"
            f"&start%5Bhour%5D={start.strftime('%H')}"
            f"&end%5Bdate%5D={now.strftime('%d.%m.%Y')}"
            f"&end%5Bhour%5D={now.strftime('%H')}"
        )
        return CSV_URL.format(station=self._station) + params

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch and parse CSV, returning latest sample with mapped pollutants."""
        url = self._build_url()
        try:
            async with self._session.get(url, timeout=ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                text = await resp.text()
        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(f"HTTP error while fetching {url}: {err}") from err

        # Parse CSV (semicolon separated; headers in German)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 5:
            raise UpdateFailed("CSV response missing data rows")

        data_lines = lines[4:]
        # Find latest row with values (ignore rows with all empty values)
        latest: dict[str, Any] | None = None
        for raw in reversed(data_lines):
            parts = raw.split(";")
            if not parts or len(parts) < 8:
                continue
            # parts: [timestamp, PM10, PM2_5, NO2, NOx, NO, O3, SO2]
            ts = parts[0]
            try:
                # Validate timestamp format
                datetime.strptime(ts, "%d.%m.%Y %H:%M")
            except ValueError:
                continue
            # If all pollutant fields empty, skip
            if all(p == "" for p in parts[1:8]):
                continue

            def to_float(val: str) -> float | None:
                try:
                    return float(val) if val != "" else None
                except ValueError:
                    return None

            latest = {
                "timestamp": ts,
                "pm10": to_float(parts[1]),
                "pm25": to_float(parts[2]),
                "no2": to_float(parts[3]),
                "nox": to_float(parts[4]),
                "no": to_float(parts[5]),
                "o3": to_float(parts[6]),
                "so2": to_float(parts[7]),
            }
            break

        if latest is None:
            raise UpdateFailed("No valid data rows in CSV")

        return latest


class LuftmessnetzCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data update coordinator for Luftmessnetz Bremen."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LuftmessnetzClient,
        config_entry: ConfigEntry,
        update_interval: timedelta = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize the coordinator with client and update interval."""
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from the API."""
        try:
            return await self.client.async_get_data()
        except UpdateFailed:
            # Already normalized; re-raise
            raise
        except Exception as err:
            raise UpdateFailed(f"Unexpected error while updating data: {err}") from err
