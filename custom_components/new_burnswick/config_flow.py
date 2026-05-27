"""Config flow for New Brunswick Burn Ban Status integration."""

import logging

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_COUNTY, COUNTIES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NewBurnswickConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for New Brunswick Burn Ban Status."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            counties = user_input[CONF_COUNTY]

            # If "all" is checked, we select all counties
            if "all" in counties:
                counties = COUNTIES

            if not counties:
                errors["base"] = "no_counties_selected"
            else:
                await self.async_set_unique_id("new_burnswick_config")
                self._abort_if_unique_id_configured()

                # Save the processed counties list in data
                user_input[CONF_COUNTY] = counties
                return self.async_create_entry(
                    title="New Brunswick Burn Ban Status", data=user_input
                )

        # Build options dictionary with a "Select All" entry
        county_options = {"all": "Select All"}
        county_options.update({c: c.title() for c in COUNTIES})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COUNTY): cv.multi_select(county_options),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return NewBurnswickOptionsFlowHandler()


class NewBurnswickOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for New Brunswick Burn Ban Status."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            counties = user_input[CONF_COUNTY]

            if "all" in counties:
                counties = COUNTIES

            if not counties:
                errors["base"] = "no_counties_selected"
            else:
                return self.async_create_entry(title="", data={CONF_COUNTY: counties})

        # Pre-select already configured counties
        current_counties = self.config_entry.options.get(
            CONF_COUNTY, self.config_entry.data.get(CONF_COUNTY, [])
        )

        county_options = {"all": "Select All"}
        county_options.update({c: c.title() for c in COUNTIES})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_COUNTY,
                        default=current_counties,
                    ): cv.multi_select(county_options),
                }
            ),
            errors=errors,
        )
