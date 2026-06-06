"""Tests for New Brunswick Burn Ban Status binary sensors."""

from unittest.mock import MagicMock

from custom_components.new_burnswick.binary_sensor import NewBurnswickFireAllowedSensor


def test_fire_allowed_sensor_properties():
    """Test the properties of the fire allowed binary sensor."""
    coordinator = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    county = "YORK"

    coordinator.data = {
        "YORK": {
            "NAME": "YORK",
            "VALIDDATE": 1705312800000,
            "PUBLICCATEGORY": 3,
            "OTHER": "DATA",
        }
    }

    sensor = NewBurnswickFireAllowedSensor(coordinator, entry, county)

    assert sensor.unique_id == "test_entry_york_burning_currently_allowed"
    assert sensor.is_on is True  # Category 3 is always allowed
    assert sensor.extra_state_attributes["county"] == "York"
    assert sensor.extra_state_attributes["api_attributes"] == coordinator.data["YORK"]
    assert sensor.extra_state_attributes["burn_category"] == 3
    assert sensor.name == "Burning Currently Allowed"
