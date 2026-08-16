import os
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

os.environ.setdefault("HLL_MAINTENANCE_CONTAINER", "1")
os.environ.setdefault("SERVER_NUMBER", "1")

from rcon.game.hll.profile import HLL_PROFILE
from rcon.game.hllv.profile import HLLV_PROFILE
from rcon.logs.loop import LogLoop
from rcon.maps import GameMode
from rcon.utils import default_player_info_dict

OFFENSIVE_MAP = "carentan_offensive_us"


def make_map_info(*, end=None, match_time=0):
    return {
        "name": OFFENSIVE_MAP,
        "start": 1_000,
        "end": end,
        "guessed": False,
        "player_stats": {},
        "game_layout": {"requested": [], "set": []},
        "cap_flips": [{"allied_score": 0, "axis_score": 5, "ts": 0}],
        "match_time": match_time,
    }


def make_gamestate(
    *, map_id=OFFENSIVE_MAP, remaining=1_798, allied_score=1, axis_score=4
):
    return {
        "current_map": {"id": map_id},
        "game_mode": GameMode.OFFENSIVE,
        "time_remaining": timedelta(seconds=remaining),
        "match_time": 5_400,
        "allied_score": allied_score,
        "axis_score": axis_score,
    }


def make_loop(gamestate):
    loop = object.__new__(LogLoop)
    loop.ACTIVE_MAP_INDEX = 0
    loop.CURR_MAP_END = 0
    loop.now = 1_002
    loop.rcon = Mock()
    loop.rcon.game_profile = HLL_PROFILE
    loop.rcon.get_gamestate.return_value = gamestate
    loop.get_detailed_players = Mock(return_value={"players": {}, "fail_count": 0})
    loop.record_player_stats = Mock()
    return loop


@patch("rcon.logs.loop.MapsHistory")
def test_ended_match_is_not_mutated_by_next_match_score(maps_history_cls):
    current_map = make_map_info(end=1_100, match_time=9_000)
    history = maps_history_cls.return_value
    history.get_current_map.return_value = current_map
    loop = make_loop(make_gamestate(allied_score=5, axis_score=0))

    elapsed = loop.update_maps_history(prev_map_time_elapsed=98)

    assert elapsed == 2
    assert current_map["cap_flips"] == [
        {"allied_score": 0, "axis_score": 5, "ts": 0}
    ]
    loop.get_detailed_players.assert_called_once()
    history.update.assert_called_once_with(0, current_map)


@patch("rcon.logs.loop.MapsHistory")
def test_live_map_mismatch_does_not_record_cap_flip(maps_history_cls):
    current_map = make_map_info(match_time=9_000)
    history = maps_history_cls.return_value
    history.get_current_map.return_value = current_map
    loop = make_loop(make_gamestate(map_id="foy_offensive_ger"))

    elapsed = loop.update_maps_history(prev_map_time_elapsed=98)

    assert elapsed == 0
    assert len(current_map["cap_flips"]) == 1
    loop.get_detailed_players.assert_not_called()
    history.update.assert_not_called()


@patch("rcon.logs.loop.MapsHistory")
def test_offensive_match_time_normalizes_broken_server_default(maps_history_cls):
    current_map = make_map_info()
    history = maps_history_cls.return_value
    history.get_current_map.return_value = current_map
    loop = make_loop(make_gamestate())

    elapsed = loop.update_maps_history(prev_map_time_elapsed=1)

    assert elapsed == 2
    assert current_map["match_time"] == 9_000
    assert current_map["cap_flips"][-1] == {
        "allied_score": 1,
        "axis_score": 4,
        "ts": 2,
    }
    assert history.update.call_count == 2
    history.update.assert_called_with(0, current_map)


@pytest.mark.parametrize(
    ("map_name", "initial_score", "later_score"),
    (
        ("carentan_offensive_us", (0, 5), (1, 4)),
        ("carentan_offensive_ger", (5, 0), (4, 1)),
    ),
)
def test_offensive_initial_score_cannot_be_recorded_again(
    map_name, initial_score, later_score
):
    current_map = make_map_info()
    current_map["name"] = map_name
    current_map["cap_flips"] = []
    loop = object.__new__(LogLoop)
    loop.rcon = Mock(game_profile=HLL_PROFILE)

    gs = make_gamestate(
        map_id=map_name,
        allied_score=initial_score[0],
        axis_score=initial_score[1],
    )
    loop.record_cap_flips(current_map, 0, gs)

    gs["allied_score"], gs["axis_score"] = later_score
    loop.record_cap_flips(current_map, 300, gs)

    gs["allied_score"], gs["axis_score"] = initial_score
    loop.record_cap_flips(current_map, 600, gs)

    assert current_map["cap_flips"] == [
        {
            "allied_score": initial_score[0],
            "axis_score": initial_score[1],
            "ts": 0,
        },
        {
            "allied_score": later_score[0],
            "axis_score": later_score[1],
            "ts": 300,
        },
    ]


@pytest.mark.parametrize(
    ("team", "expected_team_id"),
    (("allies", 1), ("axis", 2)),
)
def test_hllv_player_stats_use_normalized_logical_team_ids(
    team, expected_team_id
):
    loop = object.__new__(LogLoop)
    loop.rcon = Mock(game_profile=HLLV_PROFILE)
    loop.now = 2_000
    loop.RECORD_PLAYER_STATS_DELAY = 120
    current_map = make_map_info()
    player = default_player_info_dict()
    player.update(
        {
            "name": "Vietnam Player",
            "player_id": "player-id",
            "team": team,
            "role": "specialist",
            "unit_id": 3,
            "level": 10,
        }
    )
    detailed_players = {
        "players": {"player-id": player},
        "fail_count": 0,
    }

    # The first sample creates the cache entry; the next records its unit.
    loop.record_player_stats(current_map, 10, detailed_players)
    loop.record_player_stats(current_map, 20, detailed_players)

    unit = current_map["player_stats"]["player-id"]["p_unit"]
    assert unit == {
        "ts": 20,
        "team": expected_team_id,
        "squad": 3,
        "role": 5,
    }
