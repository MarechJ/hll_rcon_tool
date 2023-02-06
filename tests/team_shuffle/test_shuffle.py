import pytest
from hypothesis import given
from hypothesis.strategies import composite, integers, lists, text, uuids
from rcon.team_shuffle.constants import (
    SHUFFLE_METHOD_PLAYER_LEVEL,
    SHUFFLE_METHOD_RANDOMLY,
)
from rcon.team_shuffle.shuffle import (
    find_players_to_swap_player_level,
    find_players_to_swap_randomly,
    find_players_to_swap_split_shuffle,
)

names = text(min_size=1)
# A proxy for steam IDs since they need to be unique
steam_ids = uuids()
levels = integers(min_value=1, max_value=500)


@composite
def detailed_player(draw):
    name = draw(names)
    level = draw(levels)
    steam_id_64 = draw(steam_ids)

    return {"name": name, "level": level, "steam_id_64": steam_id_64}


@pytest.mark.parametrize(
    "shuffle_function",
    [(find_players_to_swap_randomly), (find_players_to_swap_player_level)],
)
@given(
    lists(detailed_player(), min_size=0, max_size=50),
    lists(detailed_player(), min_size=0, max_size=50),
)
def test_shuffle_team_sizes(
    shuffle_function,
    team_one,
    team_two,
) -> None:
    to_swap_team_one, to_swap_team_two = shuffle_function(team_one, team_two)

    team_one_new_size = len(team_one) - len(to_swap_team_one) + len(to_swap_team_two)
    team_two_new_size = len(team_two) - len(to_swap_team_two) + len(to_swap_team_one)

    delta = abs(team_one_new_size - team_two_new_size)

    # if delta > 1:
    #     print(
    #         f"{len(team_one)=} {len(team_two)=} {len(to_swap_team_one)=} {len(to_swap_team_two)=} {team_one_new_size=} {team_two_new_size=}"
    #     )

    assert delta <= 1


@given(
    lists(detailed_player(), min_size=0, max_size=50),
    lists(detailed_player(), min_size=0, max_size=50),
)
def test_split_shuffle_team_sizes(team_one, team_two):
    to_swap_team_one, to_swap_team_two = find_players_to_swap_split_shuffle(
        team_one, team_two
    )

    team_one_new_size = len(team_one) - len(to_swap_team_one) + len(to_swap_team_two)
    team_two_new_size = len(team_two) - len(to_swap_team_two) + len(to_swap_team_one)

    delta = abs(team_two_new_size - team_one_new_size)

    if delta > 1:
        print(
            f"{len(team_one)=} {len(team_two)=} {len(to_swap_team_one)=} {len(to_swap_team_two)=} {team_one_new_size=} {team_two_new_size=}"
        )

    assert delta <= 1


@pytest.mark.parametrize(
    "team_one, team_two, expected_swapped_team_one, expected_swapped_team_two",
    [
        (
            [
                {"name": "NoodleArms", "level": 1, "steam_id_64": 1},
                {"name": "buscôO-sense", "level": 2, "steam_id_64": 2},
            ],
            [
                {"name": "Tacsquatch", "level": 3, "steam_id_64": 3},
                {"name": "Bardamus", "level": 4, "steam_id_64": 4},
            ],
            [
                {"name": "buscôO-sense", "level": 2, "steam_id_64": 2},
            ],
            [
                {"name": "Bardamus", "level": 4, "steam_id_64": 4},
            ],
        )
    ],
)
def test_player_level_shuffle_distributes_properly(
    team_one, team_two, expected_swapped_team_one, expected_swapped_team_two
):
    swapped_team_one, swapped_team_two = find_players_to_swap_player_level(
        team_one, team_two
    )

    assert team_one[1] in swapped_team_one
    assert team_two[1] in swapped_team_two
