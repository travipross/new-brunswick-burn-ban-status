"""Image platform for New Brunswick Burn Ban Status."""

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MAP_URL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # CLEANUP ORPHANED ENTITIES
    ent_reg = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(ent_reg, entry.entry_id)

    map_unique_id = f"{entry.entry_id}_burn_ban_map"

    for entity_entry in entity_entries:
        if entity_entry.domain == "image" and entity_entry.unique_id != map_unique_id:
            ent_reg.async_remove(entity_entry.entity_id)

    async_add_entities([NewBurnswickMapImageEntity(hass, coordinator, entry)], True)


class NewBurnswickMapImageEntity(CoordinatorEntity, ImageEntity):
    """Representation of the New Brunswick Burn Ban Map image."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, coordinator, entry: ConfigEntry) -> None:
        """Initialize the image entity."""
        ImageEntity.__init__(self, hass)
        CoordinatorEntity.__init__(self, coordinator)

        self.entry = entry

        # Unique ID for the image entity
        self._attr_unique_id = f"{entry.entry_id}_burn_ban_map"

        # Setting name to None ensures it takes the device name as the entity name
        self._attr_name = None

        # Associate the image with a provincial service device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_map")},
            "name": "New Brunswick Burn Ban Map",
            "manufacturer": "Government of New Brunswick",
            "model": "Burn Ban Map",
            "entry_type": "service",
        }

    @property
    def image_url(self) -> str | None:
        """Return the URL of the image."""
        if self.coordinator.last_update_success_time:
            # Use the last success timestamp as a cache-buster
            timestamp = int(self.coordinator.last_update_success_time.timestamp())
            return f"{MAP_URL}?v={timestamp}"
        return MAP_URL

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the time the image was last updated."""
        return self.coordinator.last_update_success_time

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        return {
            "image_url": self.image_url,
            "last_fetched": self.coordinator.last_update_success_time,
        }
