import unicodedata
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from hllrcon import HLLVLayer

from rcon.api_commands import (
    HLLRconAPI,
    HLLVRconAPI,
    RconAPI,
    create_rcon_api,
)
from rcon.commands import HLLServerCtl, HLLVServerCtl
from rcon.game import get_game_profile
from rcon.game.hll.profile import HLL_PROFILE
from rcon.game.hllv.profile import HLLV_PROFILE
from rcon.maps import UNKNOWN_MAP_NAME, GameMode, Team, parse_map_string
from rcon.rcon import HLLRcon, HLLVRcon, Rcon, create_rcon
from rcon.types import GameEnum, GameIntEnum, ServerInfo
from rcon.utils import guess_map_from_log


def _response(content_dict):
    return SimpleNamespace(content_dict=content_dict)


def _session(map_id: str, game_mode: str = "Warfare") -> dict:
    return {
        "remainingMatchTime": 3600,
        "gameMode": game_mode,
        "mapId": map_id,
        "axisScore": 1,
        "axisFaction": 2,
        "axisPlayerCount": 40,
        "alliedScore": 3,
        "alliedFaction": 4,
        "alliedPlayerCount": 42,
        "alliedMorale": 5,
        "axisMorale": 6,
        "initialMorale": 7,
        "matchTime": 5400,
        "queueCount": 2,
        "maxQueueCount": 6,
        "vipQueueCount": 1,
        "maxVipQueueCount": 2,
        "serverName": "Test server",
    }


def test_server_info_defaults_game_even_without_port():
    assert ServerInfo().game is GameEnum.HLL_WW2


@pytest.mark.parametrize(
    ("game", "expected"),
    [
        (GameEnum.HLL_WW2, HLL_PROFILE),
        (GameEnum.HLL_VIETNAM, HLLV_PROFILE),
        ("hll", HLL_PROFILE),
        ("hllv", HLLV_PROFILE),
    ],
)
def test_get_game_profile(game, expected):
    assert get_game_profile(game) is expected


def test_hllv_profile_does_not_read_hll_map_catalog():
    hll_layer = HLL_PROFILE.parse_layer("carentan_warfare")
    hllv_layer = HLLV_PROFILE.parse_layer("carentan_warfare")

    assert hll_layer.map.id == "carentan"
    assert hllv_layer.id == "carentan_warfare"
    assert hllv_layer.map.id == UNKNOWN_MAP_NAME
    assert hllv_layer.game_mode is GameMode.DOMINATION


def test_hllv_profile_loads_hllv_catalog_with_logical_sides():
    layer_id = "wdeve_offensivenva_day"
    layer = HLLV_PROFILE.parse_layer(layer_id)

    assert layer.map.id == HLLVLayer.by_id(layer_id, strict=False).map.id
    assert layer.map.allies.team is Team.ALLIES
    assert layer.map.axis.team is Team.AXIS
    assert layer.attackers is Team.AXIS


def test_hllv_profile_resolves_parsed_log_details_not_map_name_as_layer_id():
    map_name, environment, game_mode = parse_map_string(
        "MATCH START QUẢNG NGÃI Conquest"
    )

    layer = HLLV_PROFILE.resolve_layer(
        map_name=map_name,
        game_mode=game_mode,
        environment=environment,
    )

    assert layer.id == "wdevb_conquest_day"
    assert layer.pretty_name == "Quảng Ngãi Conquest"


def test_profiles_expose_game_specific_role_ids():
    assert HLL_PROFILE.role_ids["armycommander"] == 13
    assert HLLV_PROFILE.role_ids["armycommander"] == 20
    assert HLLV_PROFILE.role_ids["specialist"] == 5


@pytest.mark.parametrize(
    ("profile", "raw", "expected_layer_id"),
    [
        (HLL_PROFILE, "MATCH START CARENTAN WARFARE", "carentan_warfare"),
        (
            HLLV_PROFILE,
            "MATCH START CAM RANH PORT DOMINATION",
            "wdeve_domination_day",
        ),
    ],
)
def test_guess_map_from_log_uses_selected_game_catalog(profile, raw, expected_layer_id):
    assert guess_map_from_log({"raw": raw}, profile).id == expected_layer_id


def test_guess_map_from_log_does_not_fall_through_to_other_game_catalog():
    guessed = guess_map_from_log({"raw": "MATCH START CARENTAN WARFARE"}, HLLV_PROFILE)

    assert guessed.id == UNKNOWN_MAP_NAME


def test_guess_map_from_log_normalizes_unicode_map_names():
    decomposed_name = unicodedata.normalize("NFD", "THANH HÒA BRIDGE")
    guessed = guess_map_from_log(
        {"raw": f"MATCH START {decomposed_name} NVA OFFENSIVE"},
        HLLV_PROFILE,
    )

    assert guessed.id == "wdevf_offensivenva_day"


@pytest.mark.parametrize("attacker", ("US", "USA"))
def test_guess_map_from_log_selects_hllv_offensive_attacker(attacker):
    guessed = guess_map_from_log(
        {"raw": f"MATCH START THANH HÒA BRIDGE {attacker} OFFENSIVE"},
        HLLV_PROFILE,
    )

    assert guessed.id == "wdevf_offensiveus_day"


def test_profiles_only_accept_their_supported_game_modes():
    assert HLL_PROFILE.parse_game_mode("Skirmish") is GameMode.SKIRMISH
    assert HLLV_PROFILE.parse_game_mode("Domination") is GameMode.DOMINATION

    with pytest.raises(ValueError, match="not supported by the 'hll' game profile"):
        HLL_PROFILE.parse_game_mode("Domination")

    with pytest.raises(ValueError, match="not supported by the 'hllv' game profile"):
        HLLV_PROFILE.parse_game_mode("Skirmish")


@pytest.mark.parametrize("profile", [HLL_PROFILE, HLLV_PROFILE])
@pytest.mark.parametrize("game_mode", ["", "   ", "not a game mode"])
def test_parse_game_mode_or_none_returns_none_instead_of_raising(profile, game_mode):
    assert profile.parse_game_mode_or_none(game_mode) is None


@pytest.mark.parametrize(
    ("profile", "game_mode", "expected"),
    [
        (HLL_PROFILE, "Skirmish", GameMode.SKIRMISH),
        (HLLV_PROFILE, "US Offensive", GameMode.OFFENSIVE),
    ],
)
def test_parse_game_mode_or_none_still_parses_valid_modes(profile, game_mode, expected):
    assert profile.parse_game_mode_or_none(game_mode) is expected


@pytest.mark.parametrize(
    ("game", "map_id"),
    [
        (GameEnum.HLL_WW2, "carentan_warfare"),
        (GameEnum.HLL_VIETNAM, "wdeve_warfare_day"),
    ],
)
def test_game_state_falls_back_to_layer_when_game_mode_is_blank(game, map_id):
    """The server reports an empty gameMode between matches.

    That used to raise ValueError out of get_gamestate(), taking down every
    caller. The layer ID is still populated, so the mode is read back from it.
    """
    ctl_type = HLLServerCtl if game is GameEnum.HLL_WW2 else HLLVServerCtl
    ctl = ctl_type(ServerInfo(game=game), Mock())
    ctl.exchange = Mock(
        side_effect=[
            _response(_session(map_id, "")),
            _response({"mAPS": [{"iD": map_id}], "currentIndex": 0}),
        ]
    )

    game_state = ctl.get_gamestate()

    assert game_state["game_mode"] is GameMode.WARFARE
    assert game_state["current_map"]["id"] == map_id


@pytest.mark.parametrize(
    ("game", "game_mode", "expected_map_id"),
    [
        (GameEnum.HLL_WW2, "Warfare", "carentan"),
        (GameEnum.HLL_VIETNAM, "Domination", UNKNOWN_MAP_NAME),
    ],
)
def test_server_ctl_parses_game_state_with_selected_profile(
    game, game_mode, expected_map_id
):
    ctl_type = HLLServerCtl if game is GameEnum.HLL_WW2 else HLLVServerCtl
    ctl = ctl_type(ServerInfo(game=game), Mock())
    ctl.exchange = Mock(
        side_effect=[
            _response(_session("carentan_warfare", game_mode)),
            _response(
                {
                    "mAPS": [{"iD": "carentan_warfare"}],
                    "currentIndex": 0,
                }
            ),
        ]
    )

    game_state = ctl.get_gamestate()

    assert game_state["current_map"]["map"]["id"] == expected_map_id
    assert game_state["next_map"]["map"]["id"] == expected_map_id
    assert game_state["next_map"]["id"] == "carentan_warfare"
    assert game_state["game_mode"] is GameMode(game_mode.lower())


def test_game_specific_controller_surface():
    hll = HLLServerCtl(ServerInfo(game=GameEnum.HLL_WW2), Mock())
    hllv = HLLVServerCtl(ServerInfo(game=GameEnum.HLL_VIETNAM), Mock())

    for method_name in (
        "get_map_sequence",
        "set_game_layout",
        "set_dynamic_weather_enabled",
    ):
        assert callable(getattr(hll, method_name))
        assert callable(getattr(hllv, method_name))


def test_hll_set_game_layout_uses_objective_names():
    ctl = HLLServerCtl(ServerInfo(game=GameEnum.HLL_WW2), Mock())
    ctl.exchange = Mock(return_value=_response({}))
    objectives = ["one", "two", "three", "four", "five"]

    result = ctl.set_game_layout(objectives)

    ctl.exchange.assert_called_once_with(
        "SetSectorLayout",
        2,
        {
            "Sector_1": "one",
            "Sector_2": "two",
            "Sector_3": "three",
            "Sector_4": "four",
            "Sector_5": "five",
        },
    )
    assert result == objectives


def test_hllv_set_game_layout_accepts_an_explicit_map():
    ctl = HLLVServerCtl(ServerInfo(game=GameEnum.HLL_VIETNAM), Mock())
    ctl.exchange = Mock(return_value=_response({}))

    result = ctl.set_game_layout("map-id", [0, 1, 2, 1, 0])

    ctl.exchange.assert_called_once_with(
        "SetSectorLayout",
        2,
        {
            "MapId": "map-id",
            "Sector_1": 0,
            "Sector_2": 1,
            "Sector_3": 2,
            "Sector_4": 1,
            "Sector_5": 0,
        },
    )
    assert result == [0, 1, 2, 1, 0]


def test_hllv_get_game_layouts_returns_server_entries():
    ctl = HLLVServerCtl(ServerInfo(game=GameEnum.HLL_VIETNAM), Mock())
    entries = [
        {"mapId": "wdevc_warfare_day", "sectors": [0, 1, 2, 1, 0]},
        {"mapId": "wdeve_domination_day", "sectors": [2, 1, 0, 1, 2]},
    ]
    ctl.exchange = Mock(return_value=_response({"entries": entries}))

    result = ctl.get_game_layouts()

    ctl.exchange.assert_called_once_with("GetSectorLayout", 2)
    assert result == entries


@pytest.mark.parametrize(
    ("map_name", "expected"),
    [
        ("wdevc_warfare_day", [0, 1, 2, 1, 0]),
        ("missing_layer", None),
    ],
)
def test_hllv_get_game_layout_returns_matching_sectors_or_none(map_name, expected):
    ctl = HLLVServerCtl(ServerInfo(game=GameEnum.HLL_VIETNAM), Mock())
    ctl.exchange = Mock(
        return_value=_response(
            {
                "entries": [
                    {
                        "mapId": "wdevc_warfare_day",
                        "sectors": [0, 1, 2, 1, 0],
                    }
                ]
            }
        )
    )

    result = ctl.get_game_layout(map_name)

    ctl.exchange.assert_called_once_with("GetSectorLayout", 2)
    assert result == expected


def test_hllv_get_objective_rows_uses_core_map_sector_definitions():
    ctl = object.__new__(HLLVRcon)
    ctl.exchange = Mock()

    result = ctl.get_objective_rows("wdeve_conquest_day")

    assert result == [
        ["Pol Storage", "Signal Site", "Pol Jetty"],
        ["Roadside Camp", "Checkpoint", "Ammo Pier"],
        ["Cantonment Outskirts", "Base Camp", "Delong Piers"],
        ["Desert Jungle Crossing", "Dry Creek Bed", "Storage Yard"],
        ["Jungle Hill", "Maintenance Market", "Communications Centre"],
    ]
    ctl.exchange.assert_not_called()


@pytest.mark.parametrize(
    "layer_id",
    [
        "wdevc_warfare_day",
        "wdevc_offensivenva_day",
        "wdevc_offensiveus_day",
        "wdevc_domination_day",
        "wdevc_conquest_day",
    ],
)
def test_hllv_get_objective_rows_accepts_supported_layer_id(layer_id):
    ctl = object.__new__(HLLVRcon)

    result = ctl.get_objective_rows(layer_id)

    assert result[0] == [
        "Market Town",
        "Riverside Plantation",
        "Hidden Encampment",
    ]
    assert len(result) == 5
    assert all(len(row) == 3 for row in result)


@pytest.mark.parametrize("map_name", ["WDEV_E", "not-a-map"])
def test_hllv_get_objective_rows_rejects_non_layer_id(map_name):
    ctl = object.__new__(HLLVRcon)

    with pytest.raises(ValueError, match="Unknown HLL Vietnam layer ID"):
        ctl.get_objective_rows(map_name)


def test_shared_game_layout_generator_uses_supplied_objective_rows():
    ctl = object.__new__(Rcon)
    rows = [
        ["a1", "a2", "a3"],
        ["b1", "b2", "b3"],
        ["c1", "c2", "c3"],
        ["d1", "d2", "d3"],
        ["e1", "e2", "e3"],
    ]

    result = ctl._generate_game_layout(
        ["left", 1, "right", "mid", 0],
        rows,
    )

    assert result == ["a1", "b2", "c3", "d2", "e1"]


def test_hllv_rcon_generates_then_serializes_integer_layout():
    ctl = object.__new__(HLLVRcon)
    ctl.exchange = Mock(return_value=_response({}))
    ctl._cache_game_layout = Mock()

    layer_id = "wdeve_conquest_day"
    result = ctl.set_game_layout(layer_id, ["left", 1, "right", "mid", 0])

    ctl.exchange.assert_called_once_with(
        "SetSectorLayout",
        2,
        {
            "MapId": layer_id,
            "Sector_1": 0,
            "Sector_2": 1,
            "Sector_3": 2,
            "Sector_4": 1,
            "Sector_5": 0,
        },
    )
    ctl._cache_game_layout.assert_called_once_with(
        ["left", 1, "right", "mid", 0],
        [
            "Pol Storage",
            "Checkpoint",
            "Delong Piers",
            "Dry Creek Bed",
            "Jungle Hill",
        ],
    )
    assert result == [
        "Pol Storage",
        "Checkpoint",
        "Delong Piers",
        "Dry Creek Bed",
        "Jungle Hill",
    ]


@pytest.mark.parametrize(
    ("game", "expected_type"),
    [
        (GameEnum.HLL_WW2, HLLRcon),
        (GameEnum.HLL_VIETNAM, HLLVRcon),
    ],
)
def test_rcon_factory_selects_concrete_game_controller(
    monkeypatch, game, expected_type
):
    monkeypatch.setattr(Rcon, "__init__", lambda self, *args, **kwargs: None)

    ctl = create_rcon(ServerInfo(game=game))

    assert type(ctl) is expected_type
    assert ctl.game_test_command() is game


def test_concrete_rcon_classes_share_commands_but_identify_their_game():
    for method_name in (
        "get_map_sequence",
        "get_objective_rows",
        "set_game_layout",
        "set_dynamic_weather_enabled",
    ):
        assert hasattr(HLLRcon, method_name)
        assert hasattr(HLLVRcon, method_name)

    assert HLLRcon.game_test_command(None) is GameEnum.HLL_WW2
    assert HLLVRcon.game_test_command(None) is GameEnum.HLL_VIETNAM
    assert HLLRcon.set_game_layout is not HLLServerCtl.set_game_layout
    assert HLLVRcon.set_game_layout is not HLLVServerCtl.set_game_layout


@pytest.mark.parametrize(
    ("game", "expected_type"),
    [
        (GameEnum.HLL_WW2, HLLRconAPI),
        (GameEnum.HLL_VIETNAM, HLLVRconAPI),
    ],
)
def test_rcon_api_factory_selects_concrete_game_controller(
    monkeypatch, game, expected_type
):
    monkeypatch.setattr(RconAPI, "__init__", lambda self, *args, **kwargs: None)

    ctl = create_rcon_api(ServerInfo(game=game))

    assert type(ctl) is expected_type
    assert ctl.game_test_command() is game


def test_api_classes_share_commands_and_keep_concrete_game_identity():
    assert hasattr(HLLRconAPI, "get_map_sequence")
    assert hasattr(HLLRconAPI, "set_dynamic_weather_enabled")
    assert hasattr(HLLVRconAPI, "get_map_sequence")
    assert hasattr(HLLVRconAPI, "set_dynamic_weather_enabled")
    assert HLLRconAPI.game_test_command(None) is GameEnum.HLL_WW2
    assert HLLVRconAPI.game_test_command(None) is GameEnum.HLL_VIETNAM
    assert HLLRconAPI.set_game_layout is HLLRcon.set_game_layout
    assert HLLVRconAPI.set_game_layout is HLLVRcon.set_game_layout


def test_timer_commands_validate_mode_against_profile():
    ctl = HLLVServerCtl(ServerInfo(game=GameEnum.HLL_VIETNAM), Mock())
    ctl.exchange = Mock()

    ctl.set_match_timer("Domination", 30)
    ctl.exchange.assert_called_once_with(
        "SetMatchTimer", 2, {"GameMode": "domination", "MatchLength": 30}
    )

    with pytest.raises(ValueError, match="not supported by the 'hllv' game profile"):
        ctl.set_match_timer(GameMode.SKIRMISH, 30)


@pytest.mark.parametrize("game", list(GameEnum))
def test_game_enum_survives_a_round_trip_through_its_stored_int(game):
    """Maps.game persists a GameIntEnum, so reading a row back needs both ways."""
    assert GameEnum.from_int(game.to_int()) is game


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        (GameIntEnum.HLL_WW2, GameEnum.HLL_WW2),
        (GameIntEnum.HLL_VIETNAM, GameEnum.HLL_VIETNAM),
    ],
)
def test_game_enum_from_int_accepts_the_values_stored_in_the_database(stored, expected):
    assert GameEnum.from_int(int(stored)) is expected


def test_layer_id_from_another_game_degrades_to_a_placeholder():
    """Why a stored map name has to be resolved against the game it was played on.

    The WWII catalog has no Vietnam IDs, so it synthesises a layer from the ID
    itself -- a title-cased name and WWII factions -- rather than failing. Any
    reader that ignores the recorded game silently shows that placeholder.
    """
    stored = "wdevc_warfare_day"

    placeholder = HLL_PROFILE.parse_layer(stored)
    assert placeholder.map.name == "Wdevc"
    assert placeholder.map.axis.name == "ger"

    actual = HLLV_PROFILE.parse_layer(stored)
    assert actual.pretty_name == "Hu\u1ebf Outskirts Warfare"
    assert actual.map.axis.name == "nva"
