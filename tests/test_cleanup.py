"""Tests for the registry cleanup utility."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.new_burnswick.cleanup import async_cleanup_registries
from custom_components.new_burnswick.const import DOMAIN


@pytest.fixture
def mock_hass():
    """Mock HomeAssistant."""
    return MagicMock()


@pytest.fixture
def mock_entry():
    """Mock ConfigEntry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    return entry


@pytest.mark.asyncio
async def test_async_cleanup_registries(mock_hass, mock_entry):
    """Test that async_cleanup_registries removes stale entities and devices."""
    # Mock entities
    mock_entity_map = MagicMock()
    mock_entity_map.entity_id = "image.nb_map"
    mock_entity_map.unique_id = "test_entry_id_burn_ban_map"

    mock_entity_button = MagicMock()
    mock_entity_button.entity_id = "button.nb_refresh"
    mock_entity_button.unique_id = "test_entry_id_refresh_button"

    mock_entity_york_status = MagicMock()
    mock_entity_york_status.entity_id = "sensor.nb_york_status"
    mock_entity_york_status.unique_id = "test_entry_id_york_status"

    mock_entity_york_fire = MagicMock()
    mock_entity_york_fire.entity_id = "binary_sensor.nb_york_fire"
    mock_entity_york_fire.unique_id = "test_entry_id_york_fire_allowed"

    mock_entity_kent_status = MagicMock()
    mock_entity_kent_status.entity_id = "sensor.nb_kent_status"
    mock_entity_kent_status.unique_id = "test_entry_id_kent_status"

    mock_entity_kent_fire = MagicMock()
    mock_entity_kent_fire.entity_id = "binary_sensor.nb_kent_fire"
    mock_entity_kent_fire.unique_id = "test_entry_id_kent_fire_allowed"

    entity_entries = [
        mock_entity_map,
        mock_entity_button,
        mock_entity_york_status,
        mock_entity_york_fire,
        mock_entity_kent_status,
        mock_entity_kent_fire,
    ]

    # Mock devices
    mock_device_map = MagicMock()
    mock_device_map.id = "dev_map_id"
    mock_device_map.identifiers = {(DOMAIN, "test_entry_id_map")}

    mock_device_york = MagicMock()
    mock_device_york.id = "dev_york_id"
    mock_device_york.identifiers = {(DOMAIN, "test_entry_id_york")}

    mock_device_kent = MagicMock()
    mock_device_kent.id = "dev_kent_id"
    mock_device_kent.identifiers = {(DOMAIN, "test_entry_id_kent")}

    device_entries = [
        mock_device_map,
        mock_device_york,
        mock_device_kent,
    ]

    # Mock entity and device registry get/entries methods
    mock_ent_reg = MagicMock()
    mock_dev_reg = MagicMock()

    with (
        patch(
            "custom_components.new_burnswick.cleanup.er.async_get",
            return_value=mock_ent_reg,
        ),
        patch(
            "custom_components.new_burnswick.cleanup.er.async_entries_for_config_entry",
            return_value=entity_entries,
        ),
        patch(
            "custom_components.new_burnswick.cleanup.dr.async_get",
            return_value=mock_dev_reg,
        ),
        patch(
            "custom_components.new_burnswick.cleanup.dr.async_entries_for_config_entry",
            return_value=device_entries,
        ),
    ):
        # Current counties: only York is selected. Kent is orphaned/stale.
        await async_cleanup_registries(mock_hass, mock_entry, ["YORK"])

        # Check entity cleanup: only Kent entities should be removed
        mock_ent_reg.async_remove.assert_any_call("sensor.nb_kent_status")
        mock_ent_reg.async_remove.assert_any_call("binary_sensor.nb_kent_fire")
        assert mock_ent_reg.async_remove.call_count == 2

        # Check device cleanup: only Kent device should be removed
        mock_dev_reg.async_remove_device.assert_called_once_with("dev_kent_id")
