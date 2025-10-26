"""Config flow for the Luftmessnetz Bremen integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow as HassConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_STATION as INTEGRATION_CONF_STATION, DEFAULT_STATION, DOMAIN
from .coordinator import LuftmessnetzClient

_LOGGER = logging.getLogger(__name__)

# Initial form with station selection (default DEHB002)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(INTEGRATION_CONF_STATION, default=DEFAULT_STATION): str}
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input by fetching a sample CSV for the station."""
    station = data[INTEGRATION_CONF_STATION]
    session = async_get_clientsession(hass)
    client = LuftmessnetzClient(session, station)
    try:
        sample = await client.async_get_data()
    except Exception as err:
        raise CannotConnect from err
    if not sample:
        raise CannotConnect
    return {"title": station}


class ConfigFlow(HassConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luftmessnetz Bremen."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[INTEGRATION_CONF_STATION])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
