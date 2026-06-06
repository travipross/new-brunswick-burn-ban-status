"""Tests for New Brunswick Burn Ban Status sensors."""

from datetime import datetime
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import EntityCategory

from custom_components.new_burnswick.sensor import (
    NewBurnswickNextUpdateSensor,
    NewBurnswickSensor,
)

NB_TZ = ZoneInfo("America/Moncton")


def test_next_update_sensor_properties():
    """Test the properties of the next update sensor."""
    coordinator = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"

    def mock_get_device_info(entry_id, county=None):
        if county:
            return {
                "identifiers": {("new_burnswick", f"{entry_id}_{county.lower()}")},
                "name": f"{county.title()} County",
            }
        return {
            "identifiers": {("new_burnswick", f"{entry_id}_common")},
            "name": "New Brunswick",
        }

    coordinator.get_device_info.side_effect = mock_get_device_info
    next_update = datetime(2026, 6, 2, 11, 5, 0, tzinfo=NB_TZ)
    coordinator.next_update_at = next_update

    sensor = NewBurnswickNextUpdateSensor(coordinator, entry)

    assert sensor.unique_id == "test_entry_next_burn_ban_data_update"
    assert sensor.device_class == SensorDeviceClass.TIMESTAMP
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC
    assert sensor.native_value == next_update
    assert sensor.translation_key == "next_burn_ban_update"
    assert sensor.has_entity_name is True
    assert sensor.device_info["identifiers"] == {("new_burnswick", "test_entry_common")}
    assert sensor.device_info["name"] == "New Brunswick"


def test_next_update_sensor_none():
    """Test the properties of the next update sensor when next_update_at is None."""
    coordinator = MagicMock()
    entry = MagicMock()
    coordinator.next_update_at = None

    sensor = NewBurnswickNextUpdateSensor(coordinator, entry)
    assert sensor.native_value is None


def test_burn_ban_sensor_properties():
    """Test the properties of the burn ban status sensor."""
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

    sensor = NewBurnswickSensor(coordinator, entry, county)

    assert sensor.unique_id == "test_entry_york_burn_ban_category"
    assert sensor.state == "allowed"  # Category 3
    assert sensor.extra_state_attributes["county"] == "York"
    assert sensor.extra_state_attributes["api_attributes"] == coordinator.data["YORK"]
    assert sensor.extra_state_attributes["raw_category"] == 3
    assert sensor.translation_key == "burn_ban_category"
