"""Tests for New Brunswick Burn Ban Status coordinator."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.new_burnswick import NB_TZ, NewBurnswickCoordinator


@pytest.fixture
def mock_hass():
    """Mock HomeAssistant."""
    return MagicMock()


@pytest.fixture
def mock_session():
    """Mock aiohttp ClientSession."""
    return MagicMock()


@pytest.mark.asyncio
async def test_coordinator_update_data_success(mock_hass, mock_session):
    """Test successful data update."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "features": [
            {
                "attributes": {
                    "NAME": "YORK",
                    "VALIDDATE": 1705312800000,  # Some timestamp
                    "PUBLICCATEGORY": 3,
                }
            }
        ]
    }
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch.object(coordinator, "_schedule_next_update"):
        data = await coordinator._async_update_data()
        assert data == {
            "YORK": {"NAME": "YORK", "VALIDDATE": 1705312800000, "PUBLICCATEGORY": 3}
        }
        assert coordinator.last_update_success_time is not None


@pytest.mark.asyncio
async def test_coordinator_update_data_no_data(mock_hass, mock_session):
    """Test data update with no data found."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"features": []}
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch.object(coordinator, "_schedule_next_update"):
        with pytest.raises(UpdateFailed, match="No county data found"):
            await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_coordinator_update_data_error(mock_hass, mock_session):
    """Test data update with API error."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    mock_response = AsyncMock()
    mock_response.status = 500
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch.object(coordinator, "_schedule_next_update"):
        with pytest.raises(UpdateFailed, match="Error fetching data: 500"):
            await coordinator._async_update_data()


def test_schedule_next_update_retry(mock_hass, mock_session):
    """Test scheduling a retry."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(None, retry=True)
        assert mock_track.called
        # Verify it scheduled for roughly 15 minutes from now
        args, _ = mock_track.call_args
        scheduled_time = args[2]
        now = datetime.now(tz=NB_TZ)
        assert scheduled_time > now + timedelta(minutes=14)
        assert scheduled_time < now + timedelta(minutes=16)


def test_schedule_next_update_stale(mock_hass, mock_session):
    """Test scheduling when data is stale."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    # Mock data with an old VALIDDATE
    stale_data = {"YORK": {"VALIDDATE": 1000000000000}}  # Very old

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(stale_data)
        assert mock_track.called
