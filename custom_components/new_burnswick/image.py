"""Image platform for New Brunswick Burn Ban Status."""

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, MAP_URL, UID_SUFFIX_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([NewBurnswickMapImageEntity(hass, coordinator, entry)], True)


class NewBurnswickMapImageEntity(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], ImageEntity
):
    """Representation of the New Brunswick Burn Ban Map image."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Any]]],
        entry: ConfigEntry,
    ) -> None:
        """Initialize the image entity."""
        ImageEntity.__init__(self, hass)
        CoordinatorEntity.__init__(self, coordinator)

        self.entry = entry

        # Unique ID for the image entity
        self._attr_unique_id = f"{entry.entry_id}_{UID_SUFFIX_MAP}"

        # Explicit name to complement the simplified device name
        self._attr_name = "Burn Ban Map"

        # Associate the image with a provincial service device
        self._attr_device_info = self.coordinator.get_device_info(entry.entry_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._cached_image = None
        super()._handle_coordinator_update()

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
