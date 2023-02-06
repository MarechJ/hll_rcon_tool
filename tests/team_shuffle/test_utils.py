import pytest
from datetime import datetime, timezone


from rcon.team_shuffle.utils import (
    get_player_last_swap_timestamp,
    set_player_swap_timestamp,
    get_player_session,
)

from rcon.team_shuffle.constants import SWAP_TYPE_BALANCE
from .test_balance import mock_redis

# TODO: test get_team_player_count()


@pytest.fixture
def sentinel_datetime():
    yield datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc)


@pytest.mark.parametrize(
    "player, expected_datetime",
    [
        (
            {"profile": {"sessions": [{"start": datetime(2022, 10, 6, 18, 8, 47)}]}},
            datetime(2022, 10, 6, 18, 8, 47, 0, timezone.utc),
        )
    ],
)
def test_get_player_session_does_not_change_datetime(player, expected_datetime):
    """Session datetimes should not be altered when adding time zone information."""
    timestamp = get_player_session(player, True)
    assert timestamp == expected_datetime


@pytest.mark.parametrize("steam_id_64, swap_type", [("1234", SWAP_TYPE_BALANCE)])
def test_getting_unset_players_is_sentinel_timestamp(
    steam_id_64, swap_type, mock_redis, sentinel_datetime
):
    """Players not in Redis should have the sentinel timestamp."""
    timestamp = get_player_last_swap_timestamp(
        mock_redis, steam_id_64=steam_id_64, swap_type=swap_type
    )
    assert timestamp == sentinel_datetime


@pytest.mark.parametrize(
    "steam_id_64, swap_type, timestamp",
    [("1234", SWAP_TYPE_BALANCE, datetime.now(timezone.utc))],
)
def test_setting_getting_player_timestamp_matches(
    steam_id_64, swap_type, timestamp, mock_redis
):
    """Setting and getting a timestamp should match."""
    # TODO: Good hypothesis test
    set_player_swap_timestamp(
        mock_redis, steam_id_64=steam_id_64, swap_type=swap_type, timestamp=timestamp
    )

    assert (
        get_player_last_swap_timestamp(
            mock_redis, steam_id_64=steam_id_64, swap_type=swap_type
        )
        == timestamp
    )
