from rcon import broadcast
from rcon.rcon import get_rcon
from rcon.broadcast import format_winning_map
import pytest
from unittest import mock


# This test requires an actual connection to the game server
def test_smoke_all_variables():
    ctl = get_rcon()
    var_dict = broadcast._get_vars(ctl)

    for k in var_dict.keys():
        print(k, broadcast.format_message(ctl, f"{'{'}{k}{'}'}"))


# @mock.patch("rcon.get_next_map", autospec=True, return_value="carentan_warfare")
@pytest.mark.parametrize(
    "winning_maps, expected",
    [
        ([("carentan_warfare", 2)], "Carentan Warfare (2 vote(s))"),
        ([("driel_offensive_ger", 2)], "Driel Off. AXIS (2 vote(s))"),
    ],
)
def test_format_winning_map(winning_maps, expected) -> None:
    with (
        mock.patch("rcon.game_logs.Rcon", autospec=True) as ctl,
        # mock.patch("rcon.get_next_map", return_value="carentan_warfare") as _,
    ):
        assert format_winning_map(ctl=ctl, winning_maps=winning_maps) == expected
