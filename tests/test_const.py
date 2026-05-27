"""Tests for New Brunswick Burn Ban Status constants."""

from custom_components.new_burnswick.const import (
    COLOR_MAPPING,
    COUNTIES,
    ICON_MAPPING,
    RGB_MAPPING,
    STATUS_MAPPING,
    TEXT_MAPPING,
)


def test_mappings_completeness():
    """Verify that all mappings have the same keys."""
    keys = {0, 1, 2, 3}
    assert set(STATUS_MAPPING.keys()) == keys
    assert set(ICON_MAPPING.keys()) == keys
    assert set(TEXT_MAPPING.keys()) == keys
    assert set(COLOR_MAPPING.keys()) == keys
    assert set(RGB_MAPPING.keys()) == keys


def test_counties_list():
    """Verify the counties list is not empty and contains expected values."""
    assert len(COUNTIES) == 15
    assert "YORK" in COUNTIES
    assert "ALBERT" in COUNTIES
