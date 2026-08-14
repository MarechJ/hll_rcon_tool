from collections.abc import Callable
from typing import Any, TypeAlias

from rcon.types import GameEnum

EndpointPermission: TypeAlias = str | set[str] | list[str]
EndpointDefinition: TypeAlias = tuple[EndpointPermission, list[str]]


GAME_ENDPOINTS: dict[GameEnum, dict[str, EndpointDefinition]] = {
    GameEnum.HLL_WW2: {
        "get_objective_rows": ("api.can_view_current_map", ["GET"]),
        "set_game_layout": ("api.can_change_game_layout", ["POST"]),
    },
    GameEnum.HLL_VIETNAM: {
        "get_objective_rows": ("api.can_view_current_map", ["GET"]),
        "get_game_layouts": ("api.can_view_current_map", ["GET"]),
        "get_game_layout": ("api.can_view_current_map", ["GET"]),
        "set_game_layout": ("api.can_change_game_layout", ["POST"]),
        "remove_game_layout": ("api.can_change_game_layout", ["POST"]),
    },
}


def resolve_game_endpoints(
    controller: Any,
    game: GameEnum,
) -> tuple[
    dict[Callable[..., Any], EndpointPermission],
    dict[Callable[..., Any], list[str]],
]:
    """Bind only the endpoint definitions supported by the active game."""

    permissions: dict[Callable[..., Any], EndpointPermission] = {}
    http_methods: dict[Callable[..., Any], list[str]] = {}
    for method_name, (required_permissions, allowed_methods) in GAME_ENDPOINTS[
        game
    ].items():
        method = getattr(controller, method_name)
        if not callable(method):
            raise TypeError(
                f"Configured endpoint {method_name!r} is not callable for {game.value!r}"
            )
        permissions[method] = required_permissions
        http_methods[method] = allowed_methods

    return permissions, http_methods
