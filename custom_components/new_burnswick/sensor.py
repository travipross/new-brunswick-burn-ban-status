"""Sensor platform for New Brunswick Burn Ban Status."""

from datetime import UTC, datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
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
    UID_SUFFIX_CATEGORY,
    UID_SUFFIX_NEXT_UPDATE,
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

    entities = [NewBurnswickSensor(coordinator, entry, county) for county in counties]
    entities.append(NewBurnswickNextUpdateSensor(coordinator, entry))
    async_add_entities(entities, True)


class NewBurnswickNextUpdateSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], SensorEntity
):
    """Diagnostic sensor to show the next scheduled update time."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "next_burn_ban_update"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Any]]],
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{UID_SUFFIX_NEXT_UPDATE}"

        # Associate the sensor with the provincial service device
        self._attr_device_info = self.coordinator.get_device_info(entry.entry_id)

    @property
    def native_value(self) -> datetime | None:
        """Return the state of the sensor."""
        return getattr(self.coordinator, "next_update_at", None)


class NewBurnswickSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], SensorEntity
):
    """Representation of a New Brunswick Burn Ban Status sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "burn_ban_category"

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
        self._attr_unique_id = (
            f"{entry.entry_id}_{self.county.lower()}_{UID_SUFFIX_CATEGORY}"
        )

        # Setting name to None ensures it takes the device name as the entity name
        self._attr_name = None

        # Device info to group entities by county
        self._attr_device_info = self.coordinator.get_device_info(
            entry.entry_id, self.county
        )

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
            "api_attributes": data,
        }
