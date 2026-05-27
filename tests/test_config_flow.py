"""Tests for config flow options handling."""

from unittest.mock import MagicMock

from custom_components.new_burnswick.config_flow import NewBurnswickConfigFlow


def test_async_get_options_flow_does_not_assign_read_only_config_entry_property():
    """Ensure options flow creation doesn't write to read-only config_entry property."""
    config_entry = MagicMock()
    config_entry.options = {}
    config_entry.data = {}

    options_flow = NewBurnswickConfigFlow.async_get_options_flow(config_entry)

    assert options_flow is not None
    assert getattr(options_flow, "_config_entry", None) is config_entry
