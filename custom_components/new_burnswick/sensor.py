"""Sensor platform for New Brunswick Burn Ban Status."""

from datetime import UTC, datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    COLOR_MAPPING,
    CONF_COUNTY,
    DOMAIN,
    ICON_MAPPING,
    RGB_MAPPING,
    STATUS_MAPPING,
    TEXT_MAPPING,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Read selected counties from options first, falling back to data
    counties = entry.options.get(CONF_COUNTY, entry.data.get(CONF_COUNTY, []))

    # 1. CLEANUP ORPHANED ENTITIES
    ent_reg = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(ent_reg, entry.entry_id)

    current_county_ids = [f"{entry.entry_id}_{c.lower()}_status" for c in counties]

    for entity_entry in entity_entries:
        if (
            entity_entry.domain == "sensor"
            and entity_entry.unique_id not in current_county_ids
        ):
            ent_reg.async_remove(entity_entry.entity_id)

    # 2. CLEANUP ORPHANED DEVICES
    dev_reg = dr.async_get(hass)
    device_entries = dr.async_entries_for_config_entry(dev_reg, entry.entry_id)

    current_device_ids = [f"{entry.entry_id}_{c.lower()}" for c in counties]
    current_device_ids.append(f"{entry.entry_id}_map")

    for device_entry in device_entries:
        for identifier in device_entry.identifiers:
            if identifier[0] == DOMAIN:
                if identifier[1] not in current_device_ids:
                    dev_reg.async_remove_device(device_entry.id)

    entities = [NewBurnswickSensor(coordinator, entry, county) for county in counties]
    async_add_entities(entities, True)


class NewBurnswickSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], SensorEntity
):
    """Representation of a New Brunswick Burn Ban Status sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "burn_ban_status"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Any]]],
        entry: ConfigEntry,
        county: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.county = county.upper()

        # Unique ID for the sensor
        self._attr_unique_id = f"{entry.entry_id}_{self.county.lower()}_status"

        # Setting name to None ensures it takes the device name as the entity name
        self._attr_name = None

        # Device info to group entities by county
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_{self.county.lower()}")},
            "name": f"{self.county.title()} County Burn Status",
            "manufacturer": "Government of New Brunswick",
            "model": "Burn Ban Status",
            "entry_type": "service",
        }

    @property
    def _county_data(self) -> dict[str, Any] | None:
        """Helper to get data for this specific county."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.county)

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        data = self._county_data
        if not data:
            return None

        category: int | None = data.get("PUBLICCATEGORY")
        if category is None:
            return "unknown"
        return STATUS_MAPPING.get(category, "unknown")

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        data = self._county_data
        if not data:
            return "mdi:help-network"

        category: int | None = data.get("PUBLICCATEGORY")
        if category is None:
            return "mdi:help-network"
        return ICON_MAPPING.get(category, "mdi:help-network")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        data = self._county_data
        if not data:
            return None

        category = data.get("PUBLICCATEGORY", 0)
        valid_date_ms = data.get("VALIDDATE")

        api_valid_until = None
        if valid_date_ms:
            try:
                # VALIDDATE in the GNB API represents the expiration time of the
                # current status (typically 11:00 AM Atlantic the following day).
                valid_dt = datetime.fromtimestamp(valid_date_ms / 1000.0, tz=UTC)
                api_valid_until = valid_dt.isoformat()
            except Exception as err:
                _LOGGER.warning("Failed to parse VALIDDATE timestamp: %s", err)

        return {
            "county": self.county.title(),
            "status_text": TEXT_MAPPING.get(category, "Unknown"),
            "status_color": COLOR_MAPPING.get(category, "unknown"),
            "status_rgb": RGB_MAPPING.get(category, [128, 128, 128]),
            "api_valid_until": api_valid_until,
            "raw_category": category,
            "api_payload": data,
        }
