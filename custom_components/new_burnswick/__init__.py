"""The New Brunswick Burn Ban Status integration."""

from datetime import datetime, timedelta
import logging
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .cleanup import async_cleanup_registries
from .const import (
    API_URL,
    CONF_COUNTY,
    DID_SUFFIX_COMMON,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# New Brunswick is always Atlantic Time
NB_TZ = ZoneInfo("America/Moncton")

PLATFORMS = ["sensor", "image", "binary_sensor", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up New Brunswick Burn Ban Status from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    coordinator = NewBurnswickCoordinator(hass, session)

    # Perform initial refresh but don't block setup if it fails
    # This ensures core entities (map, refresh button) are always created
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Clean up orphaned devices/entities from registry
    counties = entry.options.get(CONF_COUNTY, entry.data.get(CONF_COUNTY, []))
    await async_cleanup_registries(hass, entry, counties)

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


class NewBurnswickCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching New Brunswick Burn Ban data."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession) -> None:
        """Initialize the coordinator."""
        self.session = session
        self._next_update_callback: Any | None = None
        self.last_update_success_time: datetime | None = None
        self.next_update_at: datetime | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # We disable the automatic interval and manage it manually
            update_interval=None,
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from the GIS server API."""
        _LOGGER.debug("Starting API fetch from GNB GIS server.")
        try:
            # Using content_type=None in response.json() is robust against
            # incorrect Content-Type headers
            async with self.session.get(API_URL, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")

                data: dict[str, Any] = await response.json(content_type=None)
                _LOGGER.debug("API fetch successful, processing features.")
                features: list[dict[str, Any]] = data.get("features", [])

                # Map county name (in uppercase) to its attributes dictionary
                mapped_data: dict[str, dict[str, Any]] = {}
                for feature in features:
                    attributes: dict[str, Any] = feature.get("attributes", {})
                    name: str | None = attributes.get("NAME")
                    if name:
                        mapped_data[name.upper()] = attributes

                if not mapped_data:
                    raise UpdateFailed("No county data found in API response.")

                # Update the last success time
                self.last_update_success_time = utcnow()

                # Schedule the next poll based on the freshly received data
                self._schedule_next_update(mapped_data)

                return mapped_data

        except Exception as err:
            # If fetch fails, retry in 15 minutes as a fallback
            self._schedule_next_update(None, retry=True)
            raise UpdateFailed(f"Communicating with API failed: {err}") from err

    @callback
    def _schedule_next_update(
        self, data: dict[str, dict[str, Any]] | None, retry: bool = False
    ) -> None:
        """Calculate and schedule the next polling time.

        Strategy:
        - If we have a VALIDDATE in the future, sleep until 5 minutes after it expires.
        - If VALIDDATE is in the past (expired) or missing, poll every 15 minutes.
        """
        if self._next_update_callback:
            self._next_update_callback()
            self._next_update_callback = None

        now_nb = datetime.now(tz=NB_TZ)
        next_update: datetime | None = None

        if not retry and data:
            # All counties share the same VALIDDATE
            first_county = next(iter(data.values()))
            valid_date_ms = first_county.get("VALIDDATE")
            if valid_date_ms:
                # VALIDDATE is the expiration timestamp (usually 11:00 AM Atlantic)
                valid_dt = datetime.fromtimestamp(valid_date_ms / 1000.0, tz=NB_TZ)

                if valid_dt > now_nb:
                    # Data is valid for some time in the future.
                    # Schedule next check for 5 minutes after it expires.
                    next_update = valid_dt + timedelta(minutes=5)
                    _LOGGER.debug(
                        "Data is valid until %s. Scheduling next poll for %s.",
                        valid_dt.isoformat(),
                        next_update.isoformat(),
                    )

        if not next_update:
            # Data is expired, missing, or we're in a retry state.
            next_update = now_nb + timedelta(minutes=15)
            _LOGGER.debug(
                "Data is stale or missing. Retrying in 15 minutes: %s",
                next_update.isoformat(),
            )

        self.next_update_at = next_update
        _LOGGER.debug(
            "Next API poll scheduled for: %s Atlantic (tracked in next_update_at)",
            self.next_update_at.isoformat(),
        )
        self._next_update_callback = async_track_point_in_time(
            self.hass, self._handle_scheduled_update, next_update
        )

    async def _handle_scheduled_update(self, _now: datetime) -> None:
        """Trigger the coordinator refresh."""
        await self.async_refresh()

    def get_device_info(self, entry_id: str, county: str | None = None) -> DeviceInfo:
        """Return device info for a county or the shared map service."""
        if county:
            return DeviceInfo(
                identifiers={(DOMAIN, f"{entry_id}_{county.lower()}")},
                name=f"{county.title()} County",
                manufacturer="Government of New Brunswick",
                model="Burn Ban - County Data",
                entry_type="service",
            )

        return DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{DID_SUFFIX_COMMON}")},
            name="New Brunswick",
            manufacturer="Government of New Brunswick",
            model="Burn Ban - Province Data",
            entry_type="service",
        )
