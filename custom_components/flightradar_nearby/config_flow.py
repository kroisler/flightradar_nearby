"""Config flow for Flightradar Nearby."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_SCAN_INTERVAL,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
)


class FlightradarNearbyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Flightradar Nearby."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            lat = user_input[CONF_LATITUDE]
            lon = user_input[CONF_LONGITUDE]
            radius = user_input[CONF_RADIUS]

            if not (-90 <= lat <= 90):
                errors[CONF_LATITUDE] = "invalid_latitude"
            elif not (-180 <= lon <= 180):
                errors[CONF_LONGITUDE] = "invalid_longitude"
            elif radius <= 0:
                errors[CONF_RADIUS] = "invalid_radius"
            else:
                await self.async_set_unique_id(f"{lat}_{lon}_{radius}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Flightradar ({radius}km)",
                    data=user_input,
                )

        # Default: Home Assistant Standort
        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        schema = vol.Schema({
            vol.Required(CONF_LATITUDE, default=default_lat): vol.Coerce(float),
            vol.Required(CONF_LONGITUDE, default=default_lon): vol.Coerce(float),
            vol.Required(CONF_RADIUS, default=DEFAULT_RADIUS): vol.Coerce(int),
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
