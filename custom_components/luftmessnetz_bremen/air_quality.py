"""Air quality entities for the Luftmessnetz Bremen integration."""

from typing import Any

from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuftmessnetzCoordinator

type LuftmessnetzConfigEntry = ConfigEntry[LuftmessnetzCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LuftmessnetzConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up air quality entity from a config entry."""

    coordinator = entry.runtime_data
    async_add_entities([LuftmessnetzAirQualityEntity(entry, coordinator)])


class LuftmessnetzAirQualityEntity(
    CoordinatorEntity[LuftmessnetzCoordinator], AirQualityEntity
):
    """Representation of Luftmessnetz Bremen air quality."""

    _attr_has_entity_name = True
    _attr_translation_key = "overall"

    def __init__(
        self, entry: LuftmessnetzConfigEntry, coordinator: LuftmessnetzCoordinator
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}-air_quality"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Luftmessnetz Bremen",
        )

    @property
    def available(self) -> bool:  # type: ignore[override]
        """Return entity availability based on coordinator state."""
        return super().available

    @property
    def particulate_matter_2_5(self) -> float | int | None:
        """Return PM2.5 from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("pm25")

    @property
    def particulate_matter_10(self) -> float | int | None:
        """Return PM10 from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("pm10")

    @property
    def nitrogen_dioxide(self) -> float | int | None:
        """Return NO2 from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("no2")

    @property
    def nitrogen_monoxide(self) -> float | int | None:
        """Return NO from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("no")

    @property
    def ozone(self) -> float | int | None:
        """Return O3 from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("o3")

    @property
    def sulphur_dioxide(self) -> float | int | None:
        """Return SO2 from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("so2")

    @property
    def nitrogen_oxide(self) -> float | int | None:
        """Return NOx from latest sample."""
        data: dict[str, Any] = self.coordinator.data or {}
        return data.get("nox")
