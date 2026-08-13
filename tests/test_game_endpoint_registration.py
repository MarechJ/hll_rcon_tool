from unittest.mock import Mock

import pytest

from rcon.types import GameEnum
from rconweb.api.game_endpoints import resolve_game_endpoints


class HLLController:
    def get_objective_rows(self):
        pass

    def set_game_layout(self, objectives):
        pass


class HLLVController:
    def get_objective_rows(self, map_name):
        pass

    def get_game_layout(self):
        pass

    def set_game_layout(self, map_name, objectives):
        pass

    def remove_game_layout(self, map_name):
        pass


@pytest.mark.parametrize(
    ("controller", "game", "expected_names"),
    [
        (
            HLLController(),
            GameEnum.HLL_WW2,
            {"get_objective_rows", "set_game_layout"},
        ),
        (
            HLLVController(),
            GameEnum.HLL_VIETNAM,
            {
                "get_objective_rows",
                "get_game_layout",
                "set_game_layout",
                "remove_game_layout",
            },
        ),
    ],
)
def test_resolve_game_endpoints_only_binds_active_game_methods(
    controller, game, expected_names
):
    permissions, http_methods = resolve_game_endpoints(controller, game)

    assert {method.__name__ for method in permissions} == expected_names
    assert permissions.keys() == http_methods.keys()


def test_resolve_game_endpoints_rejects_missing_configured_method():
    with pytest.raises(AttributeError):
        resolve_game_endpoints(Mock(spec=HLLController), GameEnum.HLL_VIETNAM)
