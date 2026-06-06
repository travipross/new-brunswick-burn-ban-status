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
    "homeassistant.data_entry_flow",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.config_validation",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.entity_registry",
    "homeassistant.helpers.event",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.const",
    "homeassistant.util",
    "homeassistant.util.dt",
    "voluptuous",
]


class MockBase:
    """Base class for mocks."""

    def __init__(self, *args, **kwargs):
        pass


class MockEntity(MockBase):
    """Mock Entity base class."""

    entity_id = None
    _attr_unique_id = None
    _attr_name = None
    _attr_device_info = None
    _attr_device_class = None
    _attr_entity_category = None
    _attr_translation_key = None
    _attr_has_entity_name = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hass = None

    @property
    def unique_id(self):
        """Return unique ID."""
        return self._attr_unique_id

    @property
    def device_info(self):
        """Return device info."""
        return self._attr_device_info

    @property
    def device_class(self):
        """Return device class."""
        return self._attr_device_class

    @property
    def entity_category(self):
        """Return entity category."""
        return self._attr_entity_category

    @property
    def translation_key(self):
        """Return translation key."""
        return self._attr_translation_key

    @property
    def has_entity_name(self):
        """Return has entity name."""
        return self._attr_has_entity_name


class MockCoordinatorEntity(MockEntity):
    """Mock CoordinatorEntity."""

    def __init__(self, coordinator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinator = coordinator

    def __class_getitem__(cls, _item):
        return cls

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        pass


class MockImageEntity(MockEntity):
    """Mock ImageEntity."""


class MockButtonEntity(MockEntity):
    """Mock ButtonEntity."""


class MockSensorEntity(MockEntity):
    """Mock SensorEntity."""


class MockBinarySensorEntity(MockEntity):
    """Mock BinarySensorEntity."""


class MockCoordinator(MockBase):
    """Mock DataUpdateCoordinator."""

    def __init__(self, hass, logger, name, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None

    def __class_getitem__(cls, _item):
        return cls


class MockConfigFlow(MockBase):
    """Mock ConfigFlow base class."""

    def __init_subclass__(cls, **kwargs):
        pass


class MockOptionsFlow(MockBase):
    """Mock OptionsFlow base class."""


for module in mock_modules:
    sys.modules[module] = MagicMock()

# Link top-level homeassistant module attrs to mocked submodules.
sys.modules["homeassistant"].config_entries = sys.modules[
    "homeassistant.config_entries"
]
sys.modules["homeassistant"].core = sys.modules["homeassistant.core"]
sys.modules["homeassistant"].data_entry_flow = sys.modules[
    "homeassistant.data_entry_flow"
]
sys.modules["homeassistant"].helpers = sys.modules["homeassistant.helpers"]


# Mock Constants and Enums
class MockEntityCategory:
    DIAGNOSTIC = "diagnostic"
    CONFIG = "config"


class MockSensorDeviceClass:
    TIMESTAMP = "timestamp"
    TEMPERATURE = "temperature"


sys.modules["homeassistant.const"].EntityCategory = MockEntityCategory
sys.modules["homeassistant.components.sensor"].SensorDeviceClass = MockSensorDeviceClass

# Specifically mock classes and functions
sys.modules[
    "homeassistant.helpers.update_coordinator"
].DataUpdateCoordinator = MockCoordinator
sys.modules[
    "homeassistant.helpers.update_coordinator"
].CoordinatorEntity = MockCoordinatorEntity
sys.modules["homeassistant.components.image"].ImageEntity = MockImageEntity
sys.modules["homeassistant.components.button"].ButtonEntity = MockButtonEntity
sys.modules["homeassistant.components.sensor"].SensorEntity = MockSensorEntity
sys.modules[
    "homeassistant.components.binary_sensor"
].BinarySensorEntity = MockBinarySensorEntity
sys.modules["homeassistant.config_entries"].ConfigFlow = MockConfigFlow
sys.modules["homeassistant.config_entries"].OptionsFlow = MockOptionsFlow
sys.modules["homeassistant.config_entries"].ConfigEntry = MagicMock
sys.modules["homeassistant.data_entry_flow"].FlowResult = dict
sys.modules["homeassistant.helpers.config_validation"].multi_select = lambda options: (
    options
)


class UpdateFailed(Exception):
    pass


sys.modules["homeassistant.helpers.update_coordinator"].UpdateFailed = UpdateFailed


def callback(func):
    return func


sys.modules["homeassistant.core"].callback = callback
