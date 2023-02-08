import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pprint
from typing import Any, List
from unittest.mock import MagicMock

import pytest

from rcon.team_shuffle.balance import (
    check_swap_rate_limit,
    even_teams,
    find_larger_team_name,
    is_player_swappable,
)
from rcon.team_shuffle.constants import ALLIED_TEAM, AXIS_TEAM, SWAP_TYPE_EVEN_TEAMS
from rcon.team_shuffle.models import SwapRateLimitError, TeamShuffleConfig
from rcon.team_shuffle.utils import (
    get_player_session,
    set_balance_timestamp,
    set_player_swap_timestamp,
)
from rcon.types import TeamViewPlayerType


# TODO: Should move these mocks/fixtures to a shared file
class MockRedis:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key, None)

    def set(self, key, value):
        self._data[key] = value
        return True


# TODO: Figure out how to turn this into a proper fixture
class MockRCON:
    def __init__(self, team_view=None):
        self._team_view = team_view

    def get_team_view(self):
        return self._team_view

    # TODO: Doesn't implement the dict behavior the real command does
    def get_playerids(self):
        for team in self._team_view.values():
            for squad in team["squads"].values():
                for player in squad["players"]:
                    yield (player["name"], player["steam_id_64"])

    def get_detailed_player_info(self, name):
        for team in self._team_view.values():
            for squad in team["squads"].values():
                for player in squad["players"]:
                    if player["name"] == name:
                        return player

    def do_switch_player_now(self, name, by, result="SUCCESS"):
        return result

    def do_message_player(
        self,
        player=None,
        steam_id_64=None,
        message="",
        by="",
        save_message=False,
        result="SUCCESS",
    ):
        return result


def team_view_file(path: str):
    datetime_teamview_fields = ("created", "last_seen", "start", "end")

    # With modification from https://stackoverflow.com/a/72138110
    def parse_timestamp(json_value) -> Any:
        if isinstance(json_value, str):
            return datetime.fromisoformat(json_value)
        elif isinstance(json_value, list):
            return [datetime.fromisoformat(i) for i in json_value]
        else:
            return json_value

    def object_hook(json_dict):
        result = {}
        for key, val in json_dict.items():
            if key in datetime_teamview_fields:
                real_timestamp = parse_timestamp(val)
                result[key] = real_timestamp
            else:
                result[key] = val
        return result

    with open(path) as fp:
        return json.load(fp, object_hook=object_hook)


@pytest.fixture
def mock_redis():
    yield MockRedis()


@pytest.fixture
def mock_config():
    yield TeamShuffleConfig(
        rate_limit_sec=5,
        discord_webhook_url="",
        discord_audit_swaps=False,
        discord_audit_service_name="",
        even_teams_swap_message="",
        team_shuffle_swap_message="",
        swap_on_death_description="on death",
        swap_immediately_description="immediately",
        even_teams_logger_message="",
        shuffle_teams_logger_message="",
        failed_swap_logger_message="",
    )


def mock_get_player_profile(steam_id_64, nb_sessions, team_view):
    for team in team_view.values():
        for squad in team["squads"].values():
            for player in squad["players"]:
                if player["steam_id_64"] == steam_id_64:
                    return {"sessions": player["profile"]["sessions"]}


@pytest.fixture
def mocked_datetime(monkeypatch):
    datetime_mock = MagicMock(wrap=datetime)
    datetime_mock.now.return_value = datetime.fromisoformat("2022-10-01:13:00:01+00:00")

    monkeypatch.setattr("datetime.datetime", datetime_mock)


@pytest.mark.parametrize(
    "rate_limit, expected",
    [(5, SwapRateLimitError)],
)
def test_rate_limit_too_soon(mock_redis, rate_limit, expected):
    last_swap = datetime.now(timezone.utc) - timedelta(seconds=rate_limit - 1)
    set_balance_timestamp(mock_redis, last_swap)
    with pytest.raises(expected):
        check_swap_rate_limit(mock_redis, rate_limit)


@pytest.mark.parametrize("rate_limit", [(5)])
def test_rate_limit_okay(mock_redis, rate_limit):
    set_balance_timestamp(mock_redis, datetime(2022, 10, 1, 2, 0, 0, 0, timezone.utc))
    check_swap_rate_limit(mock_redis, rate_limit)


class TestPlayerSwapEligibility:
    @pytest.mark.parametrize(
        "player_info, immune_roles, expected",
        [
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 1,
                },
                ["tankcommander", "crewman"],
                False,
            ),
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 1,
                },
                [],
                True,
            ),
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "armycommander",
                    "level": 1,
                },
                [],
                True,
            ),
        ],
    )
    def test_should_not_swap_player_immune_role(
        self,
        mock_redis,
        player_info: TeamViewPlayerType,
        immune_roles: List[str],
        expected,
    ) -> None:
        """Players who have an immune role should not be swapped."""
        swap_time: datetime = datetime.now(timezone.utc) + timedelta(seconds=(-1))
        set_player_swap_timestamp(
            mock_redis,
            timestamp=swap_time,
            steam_id_64=player_info["steam_id_64"],
            swap_type=SWAP_TYPE_EVEN_TEAMS,
        )
        result = is_player_swappable(player_info, mock_redis, immune_roles=immune_roles)
        assert result == expected

    @pytest.mark.parametrize(
        "player_info, immune_level, expected",
        [
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 5,
                },
                10,
                False,
            ),
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 10,
                },
                10,
                False,
            ),
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 11,
                },
                10,
                True,
            ),
        ],
    )
    def test_should_not_swap_player_immune_level(
        self, mock_redis, player_info, immune_level, expected
    ) -> None:
        """Players with a level <= immune level should not be swapped."""
        swap_time: datetime = datetime.now(timezone.utc) + timedelta(seconds=(-1))
        set_player_swap_timestamp(
            mock_redis,
            timestamp=swap_time,
            steam_id_64=player_info["steam_id_64"],
            swap_type=SWAP_TYPE_EVEN_TEAMS,
        )

        result = is_player_swappable(
            player_info, mock_redis, immune_roles=[], immune_level=immune_level
        )
        assert result == expected

    @pytest.mark.parametrize(
        "player_info, immune_swap_time_threshold_secs, swapped_ago, expected",
        [
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 1,
                },
                5,
                2,
                False,
            ),
            (
                {
                    "name": "NoodleArms",
                    "steam_id_64": "01234567890123456",
                    "role": "tankcommander",
                    "level": 1,
                },
                5,
                6,
                False,
            ),
        ],
    )
    def test_should_not_swap_player_swapped_too_recently(
        self,
        mock_redis,
        player_info,
        immune_swap_time_threshold_secs,
        swapped_ago,
        expected,
    ) -> None:
        """Players swapped too recently should not be swapped."""
        swap_time: datetime = datetime.now(timezone.utc) - timedelta(
            seconds=(immune_swap_time_threshold_secs - swapped_ago)
        )
        set_player_swap_timestamp(
            mock_redis,
            timestamp=swap_time,
            steam_id_64=player_info["steam_id_64"],
            swap_type=SWAP_TYPE_EVEN_TEAMS,
        )

        result = is_player_swappable(
            player_info,
            mock_redis,
            immune_roles=[],
            immune_swap_time_threshold_secs=immune_swap_time_threshold_secs,
        )
        assert result == expected

    @pytest.mark.parametrize(
        "player, most_recent, expected_date",
        [
            ({}, True, datetime.now(timezone.utc)),
            ({}, False, datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc)),
        ],
    )
    def test_missing_player_session(self, player, most_recent, expected_date):
        """Players with missing sessions should be at the front of the list for swapping selection."""
        assert (
            get_player_session(player, most_recent) - expected_date
        ).total_seconds() < 2


@pytest.mark.parametrize(
    "path, expected",
    [
        (
            Path(
                "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_empty.json"
            ),
            AXIS_TEAM,
        )
    ],
)
def test_larger_team_is_larger(path, expected) -> None:
    """The larger team should be chosen."""
    team_view = team_view_file(path)
    larger_team_name = find_larger_team_name(team_view)

    assert larger_team_name == expected


# def test_select_most_recent_joins_should_respect_time():
#     """There should be no players who joined more recently than selected players."""
#     # TODO: would need to mock `get_player_profile`
#     pass


# def test_select_least_recent_joins_should_respect_time():
#     """There should be no players who joined less recently than selected players."""
#     # TODO: would need to mock `get_player_profile`
#     pass


# def test_select_players_arrival_time_num_choose_lte_team_size():
#     """Trying to select more players than available should select the entire team."""
#     # TODO: would need to mock `get_player_profile`
#     pass


# TODO: select random tests


@pytest.mark.parametrize("method, expected", [("nonsense_method", ValueError)])
def test_invalid_rebalance_method_fails(
    method, expected, mock_redis, mock_config
) -> None:
    """An invalid rebalance method raises a ValueError."""
    mock_rcon = MockRCON()

    with pytest.raises(expected):
        even_teams(mock_rcon, mock_redis, mock_config, method)


@pytest.mark.parametrize(
    "level, expected",
    [
        (-1, ValueError),
        (501, ValueError),
        (None, ValueError),
    ],
)
def test_invalid_immune_level_fails(level, expected, mock_redis, mock_config) -> None:
    """An invalid immune_level raises a ValueError."""
    # TODO: good candidate for hypothesis
    mock_rcon = MockRCON()
    with pytest.raises(expected):
        even_teams(mock_rcon, mock_redis, mock_config, immune_level=level)


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (-1, ValueError),
        (None, ValueError),
    ],
)
def test_invalid_immune_seconds_fails(
    seconds, expected, mock_redis, mock_config
) -> None:
    """An invalid immune_seconds raises a ValueError."""
    # TODO: good candidate for hypothesis
    with pytest.raises(expected):
        mock_rcon = MockRCON()
        even_teams(mock_rcon, mock_redis, mock_config, immune_seconds=seconds)


@pytest.mark.parametrize(
    "include_teamless, expected",
    [
        ("asdf", ValueError),
    ],
)
def test_invalid_include_teamless_fails(
    include_teamless, expected, mock_redis, mock_config
) -> None:
    """An invalid include_teamless raises a ValueError."""
    mock_rcon = MockRCON()
    with pytest.raises(expected):
        even_teams(
            mock_rcon, mock_redis, mock_config, include_teamless=include_teamless
        )


@pytest.mark.parametrize(
    "swap_on_death, expected",
    [
        # (1, ValueError),
        # (None, ValueError),
        ("asdf", ValueError),
    ],
)
def test_invalid_swap_on_death_fails(
    swap_on_death, expected, mock_redis, mock_config
) -> None:
    """An invalid swap_on_death raises a ValueError."""
    mock_rcon = MockRCON()
    with pytest.raises(expected):
        even_teams(mock_rcon, mock_redis, mock_config, swap_on_death=swap_on_death)


# test set_player_swap_timestamp
# test time between swaps


class TestAutobalanceScenarios:
    @pytest.fixture
    def mock_sleep_time(monkeypatch):
        monkeypatch.setattr("time.sleep", lambda: None)

    @pytest.mark.parametrize(
        "path",
        [
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_empty_allied_empty_teamless_players.json"
                )
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_players_teamless_players.json"
                )
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_empty_allied_players_teamless_players.json"
                )
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_players.json"
                )
            ),
        ],
    )
    def test_even_teams_teamless_players_are_distributed(
        self, path, mock_redis, mock_config
    ) -> None:
        """All teamless players should always be swapped to a team regardless of axis/allied team states."""
        print(f"{Path.cwd()=}")
        team_view = team_view_file(path)
        mock_rcon: MockRCON = MockRCON(team_view)

        pprint(team_view)

        _, _, _, _, teamless_players, swapped_teamless = even_teams(
            mock_rcon,
            mock_redis,
            mock_config,
            rebalance_method="arrival_most_recent",
            include_teamless=True,
        )

        assert len(teamless_players) == len(swapped_teamless)

    @pytest.mark.parametrize(
        "path, swap_method, include_teamless, expected_team, expected_player",
        [
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_players.json"
                ),
                "arrival_most_recent",
                True,
                AXIS_TEAM,
                "player6",
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_empty.json"
                ),
                "arrival_most_recent",
                False,
                AXIS_TEAM,
                "player6",
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_players.json"
                ),
                "arrival_least_recent",
                True,
                AXIS_TEAM,
                "player4",
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_players_allied_empty_teamless_empty.json"
                ),
                "arrival_least_recent",
                False,
                AXIS_TEAM,
                "player4",
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_empty_allied_players_teamless_players.json"
                ),
                "arrival_most_recent",
                True,
                ALLIED_TEAM,
                "player9",
            ),
            (
                Path(
                    "tests/team_shuffle/data/mocked_team_views/axis_empty_allied_players_teamless_players.json"
                ),
                "arrival_least_recent",
                True,
                ALLIED_TEAM,
                "player7",
            ),
        ],
    )
    def test_larger_team_and_teamless_players(
        self,
        path,
        swap_method,
        include_teamless,
        expected_team,
        expected_player,
        mock_redis,
        mock_config,
    ) -> None:
        """Player swapping should respect arrival times and teamless player inclusion."""
        team_view = team_view_file(path)
        mock_rcon = MockRCON(team_view)

        (
            _,
            swapped_axis_players,
            _,
            swapped_allied_players,
            teamless_players,
            swapped_teamless,
        ) = even_teams(
            mock_rcon,
            mock_redis,
            mock_config,
            swap_method,
            include_teamless=include_teamless,
        )

        if expected_team == AXIS_TEAM:
            assert swapped_axis_players[0]["name"] == expected_player
        elif expected_team == ALLIED_TEAM:
            assert swapped_allied_players[0]["name"] == expected_player

        assert len(swapped_teamless) == len(teamless_players)
