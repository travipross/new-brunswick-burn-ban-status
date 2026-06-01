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


def test_schedule_next_update_data_for_tomorrow_fresh(mock_hass, mock_session):
    """Test that data is fresh when VALIDDATE is tomorrow or later.

    This is the new behavior: data is only considered complete if VALIDDATE
    is strictly for tomorrow or later, ensuring we poll again tomorrow.
    """
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    # Create data with VALIDDATE for tomorrow
    now_nb = datetime.now(tz=NB_TZ)
    tomorrow_nb = now_nb + timedelta(days=1)
    tomorrow_11am = datetime.combine(
        tomorrow_nb.date(),
        tomorrow_nb.replace(hour=11, minute=0, second=0, microsecond=0).time(),
        tzinfo=NB_TZ,
    )
    tomorrow_timestamp_ms = int(tomorrow_11am.timestamp() * 1000)

    fresh_data = {
        "YORK": {
            "NAME": "YORK",
            "VALIDDATE": tomorrow_timestamp_ms,
            "PUBLICCATEGORY": 3,
        }
    }

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(fresh_data)
        assert mock_track.called

        # Verify it scheduled for tomorrow at 11:05 AM
        args, _ = mock_track.call_args
        scheduled_time = args[2]

        expected_time = datetime.combine(
            tomorrow_nb.date(),
            tomorrow_nb.replace(hour=11, minute=5, second=0, microsecond=0).time(),
            tzinfo=NB_TZ,
        )

        assert scheduled_time == expected_time


def test_schedule_next_update_data_for_today_not_fresh(
    mock_hass, mock_session
):
    """Test that data is NOT fresh when VALIDDATE is today.

    With the new logic, if VALIDDATE is only for today (not tomorrow+),
    it means the server hasn't published tomorrow's data yet, so we
    should retry in 15 minutes, not sleep until tomorrow.
    """
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    # Create data with VALIDDATE for today (simulating server published today's
    # data but not yet tomorrow's)
    now_nb = datetime.now(tz=NB_TZ)
    today_11am = datetime.combine(
        now_nb.date(),
        now_nb.replace(hour=11, minute=0, second=0, microsecond=0).time(),
        tzinfo=NB_TZ,
    )
    today_timestamp_ms = int(today_11am.timestamp() * 1000)

    stale_data = {
        "YORK": {
            "NAME": "YORK",
            "VALIDDATE": today_timestamp_ms,
            "PUBLICCATEGORY": 3,
        }
    }

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(stale_data)
        assert mock_track.called

        # Verify it scheduled for roughly 15 minutes from now (retry logic)
        args, _ = mock_track.call_args
        scheduled_time = args[2]
        now = datetime.now(tz=NB_TZ)

        # Should be approximately 15 minutes from now
        assert scheduled_time > now + timedelta(minutes=14)
        assert scheduled_time < now + timedelta(minutes=16)


def test_schedule_next_update_data_for_day_after_tomorrow_fresh(
    mock_hass, mock_session
):
    """Test that data is fresh when VALIDDATE is multiple days out.

    Edge case: If for some reason the server publishes data further ahead,
    we should still treat it as fresh and schedule for tomorrow.
    """
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    # Create data with VALIDDATE for 2 days from now
    now_nb = datetime.now(tz=NB_TZ)
    day_after_tomorrow_nb = now_nb + timedelta(days=2)
    day_after_tomorrow_11am = datetime.combine(
        day_after_tomorrow_nb.date(),
        day_after_tomorrow_nb.replace(hour=11, minute=0, second=0, microsecond=0).time(),
        tzinfo=NB_TZ,
    )
    timestamp_ms = int(day_after_tomorrow_11am.timestamp() * 1000)

    fresh_data = {
        "YORK": {
            "NAME": "YORK",
            "VALIDDATE": timestamp_ms,
            "PUBLICCATEGORY": 3,
        }
    }

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(fresh_data)
        assert mock_track.called

        # Verify it scheduled for tomorrow at 11:05 AM (not later)
        args, _ = mock_track.call_args
        scheduled_time = args[2]

        tomorrow_nb = now_nb + timedelta(days=1)
        expected_time = datetime.combine(
            tomorrow_nb.date(),
            tomorrow_nb.replace(hour=11, minute=5, second=0, microsecond=0).time(),
            tzinfo=NB_TZ,
        )

        assert scheduled_time == expected_time


def test_schedule_next_update_no_data(mock_hass, mock_session):
    """Test scheduling when no data is provided (None)."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(None)
        assert mock_track.called

        # Should schedule for 11:05 AM today if we haven't reached it yet,
        # or 15 minutes from now if we have passed 11:05 AM
        args, _ = mock_track.call_args
        scheduled_time = args[2]
        now = datetime.now(tz=NB_TZ)

        target_today_11 = datetime.combine(
            now.date(),
            now.replace(hour=11, minute=5, second=0, microsecond=0).time(),
            tzinfo=NB_TZ,
        )

        # Either scheduled for today's 11:05 or 15 minutes from now
        if now < target_today_11:
            assert scheduled_time == target_today_11
        else:
            assert scheduled_time > now + timedelta(minutes=14)
            assert scheduled_time < now + timedelta(minutes=16)


def test_schedule_next_update_clears_previous_callback(mock_hass, mock_session):
    """Test that previous scheduled callback is cleared."""
    coordinator = NewBurnswickCoordinator(mock_hass, mock_session)

    # Set up a mock callback
    mock_callback = MagicMock()
    coordinator._next_update_callback = mock_callback

    with patch(
        "custom_components.new_burnswick.async_track_point_in_time"
    ) as mock_track:
        coordinator._schedule_next_update(None, retry=True)

        # Verify the old callback was called to cancel
        mock_callback.assert_called_once()
        assert coordinator._next_update_callback is not None
