"""Mock Home Assistant for basic tests."""

import sys
from unittest.mock import MagicMock

# Mock Home Assistant modules
mock_modules = [
    "homeassistant",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.components.binary_sensor",
    "homeassistant.components.image",
    "homeassistant.components.button",
    "homeassistant.config_entries",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.entity_registry",
    "homeassistant.helpers.event",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.util",
    "homeassistant.util.dt",
]


class MockBase:
    """Base class for mocks."""

    def __init__(self, *args, **kwargs):
        pass


class MockCoordinator(MockBase):
    """Mock DataUpdateCoordinator."""

    def __init__(self, hass, logger, name, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None


for module in mock_modules:
    sys.modules[module] = MagicMock()

# Specifically mock classes and functions
sys.modules[
    "homeassistant.helpers.update_coordinator"
].DataUpdateCoordinator = MockCoordinator


class UpdateFailed(Exception):
    pass


sys.modules["homeassistant.helpers.update_coordinator"].UpdateFailed = UpdateFailed


def callback(func):
    return func


sys.modules["homeassistant.core"].callback = callback
