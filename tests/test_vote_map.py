from collections import Counter

import pytest

from rcon.maps import (
    MAPS,
    Environment,
    GameMode,
    Layer,
    Team,
    _parse_legacy_layer,
    get_opposite_side,
    parse_layer,
)
from rcon.vote_map import VoteMap

SMDM_WARFARE = Layer(
    id="stmariedumont_warfare",
    map=MAPS["stmariedumont"],
    game_mode=GameMode.WARFARE,
)

SME_WARFARE = Layer(
    id="stmereeglise_warfare",
    map=MAPS["stmereeglise"],
    game_mode=GameMode.WARFARE,
)


@pytest.mark.parametrize(
    "selection, maps_to_numbers, votes, total_votes, join_char, expected",
    [
        (
            [SMDM_WARFARE, SME_WARFARE],
            {SMDM_WARFARE: "0", SME_WARFARE: "1"},
            Counter(
                {
                    "Winston": SMDM_WARFARE,
                    "SodiumEnglish": SME_WARFARE,
                    "NoodleArms": SMDM_WARFARE,
                }
            ),
            3,
            "\n",
            "[0] St. Marie Du Mont Warfare - 0/3 votes\n[1] St. Mere Eglise Warfare - 0/3 votes",
        ),
    ],
)
def test_join_vote_options(
    selection, maps_to_numbers, votes, total_votes, join_char, expected
):
    assert (
        VoteMap.join_vote_options(
            selection=selection,
            maps_to_numbers=maps_to_numbers,
            ranked_votes=votes,
            total_votes=total_votes,
            join_char=join_char,
        )
        == expected
    )


@pytest.mark.parametrize(
    "selection, votes, format_type, expected",
    [
        (
            [SMDM_WARFARE, SME_WARFARE],
            {
                "Winston": SMDM_WARFARE,
                "SodiumEnglish": SME_WARFARE,
                "NoodleArms": SMDM_WARFARE,
            },
            "by_mod_vertical_all",
            "WARFARES:\n[0] St. Marie Du Mont Warfare - 2/3 votes\n[1] St. Mere Eglise Warfare - 1/3 votes",
        ),
    ],
)
def test_format_map_vote(selection, votes, format_type, expected):
    assert (
        VoteMap.format_map_vote(
            selection=selection, votes=votes, format_type=format_type
        )
        == expected
    )


@pytest.mark.parametrize(
    "team, expected",
    [
        (Team.ALLIES, Team.AXIS),
        (Team.AXIS, Team.ALLIES),
    ],
)
def test_get_opposite_side(team, expected):
    assert get_opposite_side(team) == expected


@pytest.mark.parametrize(
    "layer_name, expected",
    [
        (
            "DRL_S_1944_P_Skirmish",
            Layer(
                id="DRL_S_1944_P_Skirmish",
                map=MAPS["driel"],
                game_mode=GameMode.CONTROL,
                environment=Environment.DAWN,
            ),
        ),
        (
            "DRL_S_1944_Night_P_Skirmish",
            Layer(
                id="DRL_S_1944_Night_P_Skirmish",
                map=MAPS["driel"],
                game_mode=GameMode.CONTROL,
                environment=Environment.NIGHT,
            ),
        ),
        (
            "DRL_S_1944_Day_P_Skirmish",
            Layer(
                id="DRL_S_1944_Day_P_Skirmish",
                map=MAPS["driel"],
                game_mode=GameMode.CONTROL,
                environment=Environment.DAY,
            ),
        ),
        (
            "ELA_S_1942_P_Skirmish",
            Layer(
                id="ELA_S_1942_P_Skirmish",
                map=MAPS["driel"],
                game_mode=GameMode.CONTROL,
                environment=Environment.DAY,
            ),
        ),
        (
            "ELA_S_1942_Night_P_Skirmish",
            Layer(
                id="ELA_S_1942_Night_P_Skirmish",
                map=MAPS["driel"],
                game_mode=GameMode.CONTROL,
                environment=Environment.DUSK,
            ),
        ),
    ],
)
def test_parse_layer(layer_name, expected):
    assert parse_layer(layer_name) == expected


@pytest.mark.parametrize(
    "layer_name, expected",
    [
        (
            "elalamein_offensive_CW",
            Layer(
                id="elalamein_offensive_CW",
                map=MAPS["elalamein"],
                game_mode=GameMode.OFFENSIVE,
                attackers=Team.ALLIES,
            ),
        ),
    ],
)
def test_parse_legacy_layer(layer_name, expected):
    assert _parse_legacy_layer(layer_name) == expected
