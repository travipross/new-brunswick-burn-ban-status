"""Button platform for New Brunswick Burn Ban Status."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # CLEANUP ORPHANED ENTITIES
    ent_reg = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(ent_reg, entry.entry_id)

    refresh_unique_id = f"{entry.entry_id}_refresh_button"

    for entity_entry in entity_entries:
        if (
            entity_entry.domain == "button"
            and entity_entry.unique_id != refresh_unique_id
        ):
            ent_reg.async_remove(entity_entry.entity_id)

    async_add_entities([NewBurnswickRefreshButton(coordinator, entry)], True)


class NewBurnswickRefreshButton(CoordinatorEntity, ButtonEntity):
    """Representation of a refresh button for the Burn Ban Status."""

    _attr_has_entity_name = True
    _attr_name = "Refresh Data"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entry = entry

        # Unique ID for the button
        self._attr_unique_id = f"{entry.entry_id}_refresh_button"

        # Associate the button with the provincial service device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_map")},
            "name": "New Brunswick Burn Ban Map",
            "manufacturer": "Government of New Brunswick",
            "model": "Burn Ban Map",
            "entry_type": "service",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Manual refresh triggered via button.")
        await self.coordinator.async_request_refresh()
