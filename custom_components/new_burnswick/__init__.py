"""The New Brunswick Burn Ban Status integration."""

from datetime import datetime, timedelta
import logging
from typing import Any
from zoneinfo import ZoneInfo

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .const import (
    API_URL,
    DOMAIN,
    UPDATE_HOUR_DATA,
    UPDATE_MINUTE,
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
        """Calculate and schedule the next polling time."""
        if self._next_update_callback:
            self._next_update_callback()
            self._next_update_callback = None

        now_nb = datetime.now(tz=NB_TZ)
        next_update: datetime

        if retry:
            # Basic retry if something went wrong
            next_update = now_nb + timedelta(minutes=15)
        else:
            # Determine if the data we just got is "current"
            # (from today's update window)
            is_fresh = False
            if data:
                # All counties share the same VALIDDATE
                first_county = next(iter(data.values()))
                valid_date_ms = first_county.get("VALIDDATE")
                if valid_date_ms:
                    # VALIDDATE is 11:00 AM Atlantic (14:00 UTC)
                    valid_dt = datetime.fromtimestamp(valid_date_ms / 1000.0, tz=NB_TZ)
                    # Data is fresh if it is for today or later, and it's currently
                    # during or after the update hour
                    if valid_dt.date() >= now_nb.date():
                        is_fresh = True

            if is_fresh:
                # We have today's data. Sleep until 11:05 AM tomorrow.
                next_update = datetime.combine(
                    now_nb.date() + timedelta(days=1),
                    datetime.min.time().replace(
                        hour=UPDATE_HOUR_DATA, minute=UPDATE_MINUTE
                    ),
                    tzinfo=NB_TZ,
                )
                _LOGGER.debug(
                    "Data is fresh (VALIDDATE: %s). "
                    "Sleeping until tomorrow's update window.",
                    valid_dt.isoformat(),
                )
            else:
                # Data is old.
                target_today_11 = datetime.combine(
                    now_nb.date(),
                    datetime.min.time().replace(
                        hour=UPDATE_HOUR_DATA, minute=UPDATE_MINUTE
                    ),
                    tzinfo=NB_TZ,
                )

                if now_nb < target_today_11:
                    next_update = target_today_11
                    _LOGGER.debug("Waiting for today's 11:05 AM update window.")
                else:
                    # We are in the "waiting for server" window
                    next_update = now_nb + timedelta(minutes=15)
                    _LOGGER.debug(
                        "Data is stale. Retrying in 15 minutes to catch server update."
                    )

        _LOGGER.debug(
            "Scheduling next API poll for: %s Atlantic", next_update.isoformat()
        )

        self._next_update_callback = async_track_point_in_time(
            self.hass, self._handle_scheduled_update, next_update
        )

    async def _handle_scheduled_update(self, _now: datetime) -> None:
        """Trigger the coordinator refresh."""
        await self.async_refresh()
