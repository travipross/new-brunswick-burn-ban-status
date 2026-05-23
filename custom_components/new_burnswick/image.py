"""Image platform for New Brunswick Burn Ban Status."""
from datetime import datetime, timezone
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

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
        return "https://www3.gnb.ca/public/fire-feu/maps/cat1.png?dummy=0.4236566"

    @property
    def image_last_updated(self) -> datetime | None:
        """Return the time the image was last updated."""
        if not self.coordinator.data:
            return None
        
        # Extract VALIDDATE from any county in the response (they all share the same update date/time)
        first_county_data = next(iter(self.coordinator.data.values()), None)
        if first_county_data:
            valid_date_ms = first_county_data.get("VALIDDATE")
            if valid_date_ms:
                try:
                    return datetime.fromtimestamp(valid_date_ms / 1000.0, tz=timezone.utc)
                except Exception:
                    pass
        
        return self.coordinator.last_update_success_time
