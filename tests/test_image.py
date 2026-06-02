"""Tests for New Brunswick Burn Ban Status image platform."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from custom_components.new_burnswick.image import NewBurnswickMapImageEntity


@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    coordinator = MagicMock()
    coordinator.last_update_success_time = None

    def mock_get_device_info(entry_id, county=None):
        if county:
            return {"name": f"{county.title()} County Burn Status"}
        return {"name": "New Brunswick Burn Ban Data"}

    coordinator.get_device_info.side_effect = mock_get_device_info
    return coordinator


@pytest.fixture
def mock_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    return entry


@pytest.fixture
def mock_hass():
    """Mock HomeAssistant."""
    return MagicMock()


def test_image_entity_init(mock_hass, mock_coordinator, mock_entry):
    """Test image entity initialization."""
    entity = NewBurnswickMapImageEntity(mock_hass, mock_coordinator, mock_entry)

    assert entity.unique_id == "test_entry_burn_ban_map"
    assert entity.device_info["name"] == "New Brunswick Burn Ban Data"


def test_image_url_with_timestamp(mock_hass, mock_coordinator, mock_entry):
    """Test image_url includes a timestamp when available."""
    fixed_now = datetime(2024, 1, 1, 12, 0, 0)
    mock_coordinator.last_update_success_time = fixed_now

    entity = NewBurnswickMapImageEntity(mock_hass, mock_coordinator, mock_entry)

    expected_timestamp = int(fixed_now.timestamp())
    assert f"v={expected_timestamp}" in entity.image_url


def test_handle_coordinator_update_clears_cache(
    mock_hass, mock_coordinator, mock_entry
):
    """Test that _handle_coordinator_update clears the internal cache."""
    entity = NewBurnswickMapImageEntity(mock_hass, mock_coordinator, mock_entry)

    # Simulate a cached image
    entity._cached_image = b"some_image_data"

    # Trigger coordinator update
    entity._handle_coordinator_update()

    # Verify cache is cleared
    assert entity._cached_image is None
