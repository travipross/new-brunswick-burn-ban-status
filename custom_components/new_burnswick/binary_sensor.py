"""Binary sensor platform for New Brunswick Burn Ban Status."""
import datetime
import logging
from zoneinfo import ZoneInfo

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_COUNTY, DOMAIN

_LOGGER = logging.getLogger(__name__)

# New Brunswick is always Atlantic Time, regardless of the HA instance's timezone setting
NB_TZ = ZoneInfo("America/Moncton")

# PUBLICCATEGORY values from the GNB GIS API
_CATEGORY_RED = 1     # No burning allowed
_CATEGORY_YELLOW = 2  # Allowed 8 PM – 8 AM only
_CATEGORY_GREEN = 3   # Always allowed

# Boundary hours in Atlantic Time
_ALLOW_HOUR_START = 20  # 8 PM — burning window opens
_ALLOW_HOUR_END = 8     # 8 AM — burning window closes
_EFFECTIVE_HOUR = 14    # 2 PM — new day's conditions become effective


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    counties = entry.options.get(CONF_COUNTY, entry.data.get(CONF_COUNTY, []))

    # CLEANUP ORPHANED ENTITIES
    from homeassistant.helpers import entity_registry as er
    ent_reg = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(ent_reg, entry.entry_id)
    
    current_county_ids = [f"{entry.entry_id}_{c.lower()}_fire_allowed" for c in counties]
    
    for entity_entry in entity_entries:
        if entity_entry.domain == "binary_sensor" and entity_entry.unique_id not in current_county_ids:
            ent_reg.async_remove(entity_entry.entity_id)

    entities = [
        NewBurnswickFireAllowedSensor(coordinator, entry, county)
        for county in counties
    ]
    async_add_entities(entities, True)


def _fire_allowed_now(category: int) -> bool | None:
    """Determine if fire is currently allowed based on category and Atlantic Time."""
    now_nb = datetime.datetime.now(tz=NB_TZ)
    now_time = now_nb.time()

    if category == _CATEGORY_GREEN:
        # Green is always allowed
        return True

    if category == _CATEGORY_YELLOW:
        # Allowed from 8 PM (inclusive) through midnight and up to (not including) 8 AM
        return now_time >= datetime.time(_ALLOW_HOUR_START, 0) or now_time < datetime.time(_ALLOW_HOUR_END, 0)

    if category == _CATEGORY_RED:
        return False
    return None  # Unknown category


def _next_transition_time() -> datetime.datetime:
    """Return the next 8 AM, 2 PM, or 8 PM as a timezone-aware Atlantic Time datetime."""
    now_nb = datetime.datetime.now(tz=NB_TZ)
    today = now_nb.date()
    candidates = [
        datetime.datetime.combine(today, datetime.time(_ALLOW_HOUR_END, 0), NB_TZ),
        datetime.datetime.combine(today, datetime.time(_EFFECTIVE_HOUR, 0), NB_TZ),
        datetime.datetime.combine(today, datetime.time(_ALLOW_HOUR_START, 0), NB_TZ),
        # Fallbacks for tomorrow
        datetime.datetime.combine(
            today + datetime.timedelta(days=1), datetime.time(_ALLOW_HOUR_END, 0), NB_TZ
        ),
        datetime.datetime.combine(
            today + datetime.timedelta(days=1), datetime.time(_EFFECTIVE_HOUR, 0), NB_TZ
        ),
        datetime.datetime.combine(
            today + datetime.timedelta(days=1), datetime.time(_ALLOW_HOUR_START, 0), NB_TZ
        ),
    ]
    return min(t for t in candidates if t > now_nb)


class NewBurnswickFireAllowedSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor: is fire currently allowed in this county?"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, county: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.county = county.upper()

        self._attr_unique_id = f"{entry.entry_id}_{self.county.lower()}_fire_allowed"
        self._attr_name = "Fire Currently Allowed"

        # Share device with the status sensor for the same county
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{self.county.lower()}")},
            "name": f"{self.county.title()} County Burn Status",
            "manufacturer": "Government of New Brunswick",
            "model": "Burn Ban Status",
            "entry_type": "service",
        }

    async def async_added_to_hass(self) -> None:
        """Schedule the first state transition on load."""
        await super().async_added_to_hass()
        self._schedule_next_transition()

    @callback
    def _schedule_next_transition(self) -> None:
        """Register a one-shot timer for state boundaries.

        Uses async_track_point_in_time with an explicit Atlantic Time datetime so the
        transition fires correctly regardless of the HA instance's configured timezone.
        """
        next_time = _next_transition_time()
        _LOGGER.debug(
            "%s: Scheduling next policy transition for %s Atlantic",
            self.entity_id,
            next_time.isoformat(),
        )
        cancel = async_track_point_in_time(
            self.hass,
            self._handle_time_transition,
            next_time,
        )
        # Ensure the pending timer is cancelled if the entity is unloaded first
        self.async_on_remove(cancel)

    @callback
    def _handle_time_transition(self, now: datetime.datetime) -> None:
        """Push a state update at the boundary, then schedule the next one."""
        _LOGGER.debug("%s: Policy transition boundary reached. Updating state.", self.entity_id)
        self.async_write_ha_state()
        self._schedule_next_transition()

    @property
    def _county_data(self) -> dict | None:
        """Return coordinator data for this county."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.county)

    @property
    def is_on(self) -> bool | None:
        """Return True if fire is currently allowed."""
        data = self._county_data
        if not data:
            _LOGGER.debug("%s: No data available for state calculation", self.entity_id)
            return None
        category = data.get("PUBLICCATEGORY", 0)
        result = _fire_allowed_now(category)
        _LOGGER.debug(
            "%s: Calculated allowed status as %s (Category: %s, Time: %s Atlantic)",
            self.entity_id,
            result,
            category,
            datetime.datetime.now(tz=NB_TZ).strftime("%H:%M:%S")
        )
        return result

    @property
    def icon(self) -> str:
        """Dynamic icon based on current state."""
        if self.is_on is True:
            return "mdi:fire"
        if self.is_on is False:
            return "mdi:fire-off"
        return "mdi:help-network"

    @property
    def extra_state_attributes(self) -> dict:
        """Return context attributes."""
        data = self._county_data
        if not data:
            return {}

        category = data.get("PUBLICCATEGORY", 0)
        now_nb = datetime.datetime.now(tz=NB_TZ)
        in_time_window = (
            now_nb.time() >= datetime.time(_ALLOW_HOUR_START, 0)
            or now_nb.time() < datetime.time(_ALLOW_HOUR_END, 0)
        )

        return {
            "county": self.county.title(),
            "burn_category": category,
            "within_time_window": in_time_window,
            "time_window": f"{_ALLOW_HOUR_START}:00 – {_ALLOW_HOUR_END:02d}:00 (yellow status only)",
            "evaluated_timezone": "America/Moncton",
        }
