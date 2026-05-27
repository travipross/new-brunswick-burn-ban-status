"""Cleanup registry helpers for New Brunswick Burn Ban Status."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_cleanup_registries(
    hass: HomeAssistant, entry: ConfigEntry, current_counties: list[str]
) -> None:
    """Remove orphaned devices and entities belonging to this config entry."""
    _LOGGER.debug("Starting registry cleanup for config entry %s", entry.entry_id)

    # 1. CLEANUP ORPHANED ENTITIES
    # Derive the set of expected unique_ids for this entry
    expected_entity_ids = {
        f"{entry.entry_id}_burn_ban_map",
        f"{entry.entry_id}_refresh_button",
    }
    for county in current_counties:
        county_lower = county.lower()
        expected_entity_ids.add(f"{entry.entry_id}_{county_lower}_status")
        expected_entity_ids.add(f"{entry.entry_id}_{county_lower}_fire_allowed")

    ent_reg = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(ent_reg, entry.entry_id)

    for entity_entry in entity_entries:
        if entity_entry.unique_id not in expected_entity_ids:
            _LOGGER.info(
                "Removing orphaned entity: %s (unique_id: %s)",
                entity_entry.entity_id,
                entity_entry.unique_id,
            )
            ent_reg.async_remove(entity_entry.entity_id)

    # 2. CLEANUP ORPHANED DEVICES
    expected_device_ids = {f"{entry.entry_id}_map"}
    for county in current_counties:
        expected_device_ids.add(f"{entry.entry_id}_{county.lower()}")

    dev_reg = dr.async_get(hass)
    device_entries = dr.async_entries_for_config_entry(dev_reg, entry.entry_id)

    for device_entry in device_entries:
        # Check if the device belongs to this integration and is no longer expected
        for identifier in device_entry.identifiers:
            if identifier[0] == DOMAIN:
                if identifier[1] not in expected_device_ids:
                    _LOGGER.info(
                        "Removing orphaned device: %s (identifier: %s)",
                        device_entry.id,
                        identifier[1],
                    )
                    dev_reg.async_remove_device(device_entry.id)
                    break
