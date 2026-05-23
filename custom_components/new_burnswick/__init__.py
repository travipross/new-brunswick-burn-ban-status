"""The New Brunswick Burn Ban Status integration."""
from datetime import timedelta
import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_URL, CONF_COUNTY, DOMAIN, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "image", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up New Brunswick Burn Ban Status from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    coordinator = NewBurnswickCoordinator(hass, session)

    # Fetch initial data so we fail early if config is invalid or server is down
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options update to reload integration
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


class NewBurnswickCoordinator(DataUpdateCoordinator):
    """Class to manage fetching New Brunswick Burn Ban data."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.session = session
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch data from the GIS server API."""
        try:
            # Using content_type=None in response.json() is robust against incorrect Content-Type headers
            async with self.session.get(API_URL, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                
                data = await response.json(content_type=None)
                features = data.get("features", [])
                
                # Map county name (in uppercase) to its attributes dictionary
                mapped_data = {}
                for feature in features:
                    attributes = feature.get("attributes", {})
                    name = attributes.get("NAME")
                    if name:
                        mapped_data[name.upper()] = attributes
                
                if not mapped_data:
                    raise UpdateFailed("No county data found in API response.")
                    
                return mapped_data

        except Exception as err:
            raise UpdateFailed(f"Communicating with API failed: {err}") from err
