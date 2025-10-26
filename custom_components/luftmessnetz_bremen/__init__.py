"""The Luftmessnetz Bremen integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_STATION
from .coordinator import LuftmessnetzClient, LuftmessnetzCoordinator

_PLATFORMS: list[Platform] = [Platform.AIR_QUALITY]

type LuftmessnetzConfigEntry = ConfigEntry[LuftmessnetzCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: LuftmessnetzConfigEntry
) -> bool:
    """Set up Luftmessnetz Bremen from a config entry."""

    session = async_get_clientsession(hass)
    station = entry.data.get(CONF_STATION)
    client = (
        LuftmessnetzClient(session, station) if station else LuftmessnetzClient(session)
    )
    coordinator = LuftmessnetzCoordinator(hass, client, entry)

    # Validate connectivity and fetch initial data before finishing setup
    await coordinator.async_config_entry_first_refresh()

    # Make the coordinator available to platforms
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: LuftmessnetzConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
