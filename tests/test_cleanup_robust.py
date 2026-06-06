"""Robust tests for New Brunswick Burn Ban Status registry cleanup."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.new_burnswick.cleanup import async_cleanup_registries
from custom_components.new_burnswick.const import (
    DID_SUFFIX_COMMON,
    UID_SUFFIX_CATEGORY,
)


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    return MagicMock()


@pytest.fixture
def mock_entry():
    """Mock Config Entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    return entry


@pytest.mark.asyncio
async def test_cleanup_registries_removes_old_and_orphaned(mock_hass, mock_entry):
    """Test that cleanup removes old-style and truly orphaned entities/devices."""
    entry_id = mock_entry.entry_id
    current_counties = ["YORK"]

    # 1. Mock Entity Registry
    mock_ent_reg = MagicMock()
    # List of entity entries currently in the registry
    old_status_entity = MagicMock(
        entity_id="sensor.york_old", unique_id=f"{entry_id}_york_status"
    )
    old_fire_entity = MagicMock(
        entity_id="binary_sensor.york_old", unique_id=f"{entry_id}_york_fire_allowed"
    )
    old_next_update = MagicMock(
        entity_id="sensor.next_old", unique_id=f"{entry_id}_next_update"
    )
    new_category_entity = MagicMock(
        entity_id="sensor.york_new", unique_id=f"{entry_id}_york_{UID_SUFFIX_CATEGORY}"
    )
    orphaned_entity = MagicMock(
        entity_id="sensor.orphaned",
        unique_id=f"{entry_id}_sunbury_{UID_SUFFIX_CATEGORY}",
    )

    mock_ent_reg.async_entries_for_config_entry.return_value = [
        old_status_entity,
        old_fire_entity,
        old_next_update,
        new_category_entity,
        orphaned_entity,
    ]

    # 2. Mock Device Registry
    mock_dev_reg = MagicMock()
    common_device = MagicMock(
        id="dev_common",
        identifiers={("new_burnswick", f"{entry_id}_{DID_SUFFIX_COMMON}")},
    )
    york_device = MagicMock(
        id="dev_york", identifiers={("new_burnswick", f"{entry_id}_york")}
    )
    orphaned_device = MagicMock(
        id="dev_orphaned", identifiers={("new_burnswick", f"{entry_id}_sunbury")}
    )

    mock_dev_reg.async_entries_for_config_entry.return_value = [
        common_device,
        york_device,
        orphaned_device,
    ]

    with (
        patch(
            "custom_components.new_burnswick.cleanup.er.async_get",
            return_value=mock_ent_reg,
        ),
        patch(
            "custom_components.new_burnswick.cleanup.er.async_entries_for_config_entry",
            return_value=mock_ent_reg.async_entries_for_config_entry(),
        ),
        patch(
            "custom_components.new_burnswick.cleanup.dr.async_get",
            return_value=mock_dev_reg,
        ),
        patch(
            "custom_components.new_burnswick.cleanup.dr.async_entries_for_config_entry",
            return_value=mock_dev_reg.async_entries_for_config_entry(),
        ),
    ):
        await async_cleanup_registries(mock_hass, mock_entry, current_counties)

    # Verify entities removed: old status, old fire, old next_update,
    # and orphaned sunbury
    removed_entities = [args[0] for args, _ in mock_ent_reg.async_remove.call_args_list]
    assert "sensor.york_old" in removed_entities
    assert "binary_sensor.york_old" in removed_entities
    assert "sensor.next_old" in removed_entities
    assert "sensor.orphaned" in removed_entities
    # New category should NOT be removed
    assert "sensor.york_new" not in removed_entities

    # Verify devices removed: orphaned sunbury
    removed_devices = [
        args[0] for args, _ in mock_dev_reg.async_remove_device.call_args_list
    ]
    assert "dev_orphaned" in removed_devices
    assert "dev_common" not in removed_devices
    assert "dev_york" not in removed_devices
