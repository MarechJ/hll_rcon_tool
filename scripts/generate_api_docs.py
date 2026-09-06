#!/usr/bin/env python3
"""Generate the static API catalog consumed by the GitHub Pages site.

The generator intentionally uses the Python AST instead of importing CRCON. Importing the
runtime initializes database-backed configuration and a game controller, while documentation
generation only needs signatures, docstrings, decorators, and endpoint registration tables.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "rconweb" / "api"
OUTPUT = ROOT / "docs" / "api-data.js"

CATEGORY_ORDER = [
    "Player actions",
    "VIP management",
    "Blacklist management",
    "General settings",
    "Maps and rotations",
    "Vote map",
    "Players and server state",
    "Admins and access",
    "Bans and profanity",
    "Messages and templates",
    "Logs and audit",
    "Scoreboards and statistics",
    "Services and automation",
    "System and authentication",
    "Configurations",
]

PLAYER_ACTIONS = {
    "bulk_message_players",
    "disband_squad",
    "disband_squad_by_name",
    "edit_player_account",
    "edit_player_soldier",
    "flag_player",
    "kick",
    "message_all_players",
    "message_player",
    "perma_ban",
    "post_player_comment",
    "punish",
    "remove_player_from_squad",
    "switch_player_now",
    "switch_player_on_death",
    "temp_ban",
    "toggle_player_watch",
    "unflag_player",
    "unwatch_player",
    "watch_player",
}

GENERAL_SETTINGS = {
    "get_autobalance_enabled",
    "get_autobalance_threshold",
    "get_dynamic_weather_enabled",
    "get_idle_autokick_time",
    "get_max_ping_autokick",
    "get_queue_length",
    "get_server_settings",
    "get_team_switch_cooldown",
    "get_vip_slots_num",
    "get_votekick_enabled",
    "get_votekick_thresholds",
    "reset_votekick_thresholds",
    "set_autobalance_enabled",
    "set_autobalance_threshold",
    "set_dynamic_weather_enabled",
    "set_idle_autokick_time",
    "set_max_ping_autokick",
    "set_queue_length",
    "set_team_switch_cooldown",
    "set_vip_slots_num",
    "set_votekick_enabled",
    "set_votekick_thresholds",
}

TITLE_OVERRIDES = {
    "get_maps": "List maps",
    "get_map": "Get current map",
    "get_next_map": "Get next map",
    "get_players": "List online players",
    "get_player_ids": "List connected player IDs",
    "get_vip_ids": "List VIPs",
    "get_blacklists": "List blacklists",
    "get_blacklist_records": "List blacklist records",
    "get_bans": "List player bans",
    "get_perma_bans": "List permanent bans",
    "get_temp_bans": "List temporary bans",
    "get_gamestate": "Get game state",
    "get_public_info": "Get public server information",
    "get_server_list": "List CRCON servers",
    "get_admin_ids": "List console admins",
    "get_admin_groups": "List console admin groups",
    "get_online_mods": "List online CRCON moderators",
    "get_ingame_mods": "List in-game moderators",
    "get_logs": "List game logs",
    "get_recent_logs": "List recent game logs",
    "get_historical_logs": "Search historical game logs",
    "get_scoreboard_maps": "List recorded matches",
    "get_live_scoreboard": "Get live player statistics",
    "get_live_game_stats": "Get live match statistics",
    "message_player": "Message a player",
    "message_all_players": "Message all players",
    "bulk_message_players": "Message multiple players",
    "switch_player_now": "Switch a player's team",
    "switch_player_on_death": "Switch a player after death",
    "post_player_comment": "Add player comment",
    "unban": "Remove player bans",
    "run_raw_command": "Run raw RCON command",
    "reconnect_gameserver": "Reconnect game server",
    "get_api_documentation": "Get live API metadata",
}

DESCRIPTION_OVERRIDES = {
    "message_player": "Show a private message in the selected player's game interface.",
    "message_all_players": "Show the same message to every player currently connected to the game server.",
    "watch_player": "Add a player to the watch list so configured integrations can report when they connect.",
    "unwatch_player": "Remove a player from the connection watch list.",
    "kick": "Immediately remove a player from the game server and record the supplied reason.",
    "punish": "Kill the selected player in-game when they are alive and show the supplied reason.",
    "switch_player_now": "Move a connected player to the opposite team immediately.",
    "switch_player_on_death": "Queue a connected player to move to the opposite team after their next death.",
    "add_vip": "Create or update a VIP entry, with an optional description and expiration time.",
    "remove_vip": "Remove a player's VIP entry from the game server.",
    "get_vip_ids": "Return the players currently registered as VIPs, including descriptions and expiration dates.",
    "get_blacklists": "Return every CRCON blacklist and its server synchronization settings.",
    "get_blacklist_records": "Search blacklist entries with player, reason, expiration, blacklist, and pagination filters.",
    "get_maps": "Return the layers supported by the active game. The optional include parameter can request objective data.",
    "get_public_info": "Return the public match snapshot used by CRCON's public scoreboard: maps, players, score, time, vote state, and server identity.",
    "get_gamestate": "Return the current and next layer, team scores, player counts, and remaining round time reported by the game server.",
    "run_raw_command": "Send a command string directly to the game server's RCON interface and return its unprocessed text response.",
    "login": "Authenticate a CRCON user with a username and password and create a browser session.",
    "logout": "End the current CRCON browser session.",
    "is_logged_in": "Report whether the current session or API key resolves to an authenticated CRCON user.",
    "do_service": "Start or stop one of CRCON's supervised background services by name.",
    "disband_squad": "Disband a squad and redeploy its members.",
    "disband_squad_by_name": "Find a squad by team and squad name, then disband it and redeploy its members.",
    "ban_profanities": "Add terms to the game server's profanity filter.",
    "unban_profanities": "Remove terms from the game server's profanity filter.",
    "temp_ban": "Immediately issue a temporary game-server ban. CRCON blacklists are preferred for managed bans.",
    "perma_ban": "Immediately issue a permanent game-server ban. CRCON blacklists are preferred for managed bans.",
    "set_auto_settings": "Save the auto-settings rule document and optionally restart its service or forward it to peer CRCON servers.",
}

RESPONSE_TYPE_OVERRIDES = {
    "get_blacklist_records": "dict[str, list[BlacklistRecordType] | int]",
    "get_chat_commands_config": "ChatCommandsUserConfig",
    "get_connection_info": "dict[str, str | int | None]",
    "get_historical_logs": "list[DBLogLineType]",
    "get_ingame_mods": "list[AdminUserType]",
    "get_kills_discord_webhooks_config": "KillsWebhooksUserConfig",
    "get_live_game_stats": "CachedLiveGameStats",
    "get_live_scoreboard": "CachedLiveGameStats",
    "get_log_stream_config": "LogStreamUserConfig",
    "get_map_history": "list[MapInfoISODates]",
    "get_online_mods": "list[AdminUserType]",
    "get_player_info": "PlayerInfoType",
    "get_players_history": "list[BasicPlayerProfileType]",
    "get_rcon_chat_commands_config": "RConChatCommandsUserConfig",
    "get_server_list": "list[dict[str, Any]]",
    "get_services": "list[dict[str, Any]]",
    "get_team_view": "dict[str, list[GetDetailedPlayer]]",
    "get_votemap_results": "list[VoteMapMapResult]",
    "get_votemap_status": "VoteMapStatus",
    "get_watch_killrate_config": "WatchKillRateUserConfig",
    "is_logged_in": "dict[str, bool]",
    "login": "bool",
    "logout": "bool",
    "set_auto_settings": "dict[str, Any]",
}


def source_tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def dotted_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Subscript):
        return f"{dotted_name(node.value)}[{ast.unparse(node.slice)}]"
    return ast.unparse(node) if node is not None else ""


def literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return ast.unparse(node)


def find_assignment(tree: ast.Module, name: str) -> ast.AST:
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == name for target in targets
        ):
            if node.value is None:
                break
            return node.value
    raise KeyError(f"Unable to find assignment {name}")


def endpoint_dict(tree: ast.Module, name: str) -> dict[str, Any]:
    value = find_assignment(tree, name)
    if not isinstance(value, ast.Dict):
        raise TypeError(f"{name} is not a dictionary")
    result: dict[str, Any] = {}
    for key, item in zip(value.keys, value.values, strict=True):
        if isinstance(key, ast.Attribute) and dotted_name(key.value) == "rcon_api":
            result[key.attr] = literal(item)
    return result


def all_functions() -> tuple[
    dict[str, ast.FunctionDef], dict[tuple[str, str], ast.FunctionDef]
]:
    plain: dict[str, ast.FunctionDef] = {}
    methods: dict[tuple[str, str], ast.FunctionDef] = {}
    paths = [
        ROOT / "rcon" / "rcon.py",
        ROOT / "rcon" / "api_commands.py",
        *API_DIR.glob("*.py"),
    ]
    for path in paths:
        tree = source_tree(path)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                plain[node.name] = node
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods[(node.name, child.name)] = child
                        if node.name in {"Rcon", "RconAPI"}:
                            plain[child.name] = child
    return plain, methods


def decorator_call(function: ast.FunctionDef, name: str) -> ast.Call | None:
    for decorator in function.decorator_list:
        if isinstance(decorator, ast.Call) and dotted_name(decorator.func).endswith(
            name
        ):
            return decorator
    return None


def type_from_name(name: str, default: ast.AST | None = None) -> str:
    if default is not None:
        value = literal(default)
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "dict[str, Any]"
    if name.startswith(("is_", "can_", "include_", "exclude_", "reset_", "forward")):
        return "bool"
    if (
        name.endswith(("_id", "_number", "_size", "_seconds", "_minutes"))
        and name != "player_id"
    ):
        return "int"
    if name in {"page", "page_size", "start", "end", "length", "seconds", "minutes"}:
        return "int"
    if name.endswith(("s", "_ids", "_names")):
        return "list[str]"
    return "str"


def inferred_data_parameters(function: ast.FunctionDef) -> list[dict[str, Any]]:
    """Find fields read from a local `data` mapping in manual Django views."""
    found: dict[str, dict[str, Any]] = {}
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "data"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            name = node.slice.value
            found[name] = {
                "name": name,
                "type": type_from_name(name),
                "required": True,
                "default": None,
            }
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "data"
            and node.func.attr == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            name = node.args[0].value
            default = node.args[1] if len(node.args) > 1 else None
            found.setdefault(
                name,
                {
                    "name": name,
                    "type": type_from_name(name, default),
                    "required": False,
                    "default": ast.unparse(default) if default is not None else "None",
                },
            )
    return list(found.values())


def function_parameters(function: ast.FunctionDef) -> list[dict[str, Any]]:
    args = [*function.args.posonlyargs, *function.args.args]
    defaults: list[ast.expr | None] = [None] * (
        len(args) - len(function.args.defaults)
    ) + list(function.args.defaults)
    params: list[dict[str, Any]] = []
    for argument, default in zip(args, defaults, strict=True):
        if argument.arg in {"self", "request", "by", "admin_name"}:
            continue
        params.append(
            {
                "name": argument.arg,
                "type": ast.unparse(argument.annotation)
                if argument.annotation
                else "any",
                "required": default is None,
                "default": None if default is None else ast.unparse(default),
            }
        )
    if function.args.kwarg:
        params.append(
            {
                "name": "configuration",
                "type": "object",
                "required": True,
                "default": None,
                "description": "Configuration fields accepted by this endpoint.",
            }
        )
    existing = {item["name"] for item in params}
    params.extend(
        item
        for item in inferred_data_parameters(function)
        if item["name"] not in existing
    )
    return params


def display_words(value: str) -> str:
    replacements = {
        "api": "API",
        "config": "configuration",
        "crcon": "CRCON",
        "csv": "CSV",
        "discord": "Discord",
        "hll": "HLL",
        "hllv": "HLLV",
        "id": "ID",
        "ids": "IDs",
        "rcon": "RCON",
        "steam": "Steam",
        "tk": "team-kill",
        "vac": "VAC",
        "vip": "VIP",
        "vips": "VIPs",
        "votemap": "vote-map",
        "votekick": "vote-kick",
    }
    return " ".join(replacements.get(word, word) for word in value.split("_"))


def endpoint_title(endpoint: str) -> str:
    if endpoint in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[endpoint]
    prefixes = {
        "add_": "Add",
        "create_": "Create",
        "delete_": "Delete",
        "describe_": "Describe",
        "download_": "Download",
        "edit_": "Update",
        "get_": "Get",
        "post_": "Add",
        "reconnect_": "Reconnect",
        "remove_": "Remove",
        "reset_": "Reset",
        "run_": "Run",
        "send_": "Send",
        "set_": "Set",
        "toggle_": "Toggle",
        "unflag_": "Remove flag from",
        "unwatch_": "Remove watch from",
        "upload_": "Upload",
        "validate_": "Validate",
        "watch_": "Watch",
    }
    for prefix, verb in prefixes.items():
        if endpoint.startswith(prefix):
            subject = display_words(endpoint.removeprefix(prefix))
            if prefix == "get_" and endpoint.removeprefix(prefix).endswith("s"):
                verb = "List"
            return f"{verb} {subject}"
    return display_words(endpoint).capitalize()


def clean_doc(function: ast.FunctionDef | None, endpoint: str) -> str:
    if endpoint in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[endpoint]
    doc = ast.get_docstring(function) if function else None
    if doc:
        return re.sub(r"\s+", " ", doc).strip()
    if endpoint.startswith("get_"):
        return f"Return the current {display_words(endpoint.removeprefix('get_'))} data from CRCON or the connected game server."
    if endpoint.startswith("set_") and endpoint.endswith("_config"):
        subject = display_words(endpoint.removeprefix("set_").removesuffix("_config"))
        return f"Validate and persist the {subject} configuration."
    if endpoint.startswith("validate_"):
        subject = display_words(
            endpoint.removeprefix("validate_").removesuffix("_config")
        )
        return f"Validate the supplied {subject} configuration without saving it."
    if endpoint.startswith("describe_"):
        subject = display_words(
            endpoint.removeprefix("describe_").removesuffix("_config")
        )
        return f"Return the JSON Schema for the {subject} configuration."
    action_descriptions = {
        "add_": "Add {subject} to CRCON or the connected game server.",
        "create_": "Create {subject} in CRCON.",
        "delete_": "Permanently delete {subject} from CRCON.",
        "download_": "Download {subject} from this CRCON server.",
        "edit_": "Update the selected {subject} in CRCON.",
        "post_": "Add {subject} to the player's CRCON record.",
        "remove_": "Remove {subject} from CRCON or the connected game server.",
        "reset_": "Restore {subject} to its initial state.",
        "send_": "Send {subject} through the connected game server.",
        "set_": "Update {subject} on CRCON or the connected game server.",
        "upload_": "Upload {subject} to this CRCON server.",
    }
    for prefix, template in action_descriptions.items():
        if endpoint.startswith(prefix):
            subject = display_words(endpoint.removeprefix(prefix))
            return template.format(subject=subject)
    title = endpoint_title(endpoint)
    return f"Use this endpoint to {title[:1].lower() + title[1:]}."


def category(endpoint: str) -> str:
    if (
        "config" in endpoint
        or endpoint.startswith("describe_")
        or "standard_messages" in endpoint
        or "auto_settings" in endpoint
    ):
        return "Configurations"
    if endpoint in PLAYER_ACTIONS:
        return "Player actions"
    if endpoint in {
        "login",
        "logout",
        "is_logged_in",
        "get_connection_info",
        "get_version",
        "get_system_usage",
        "get_api_documentation",
    }:
        return "System and authentication"
    if endpoint in GENERAL_SETTINGS:
        return "General settings"
    if "vip" in endpoint:
        return "VIP management"
    if "blacklist" in endpoint:
        return "Blacklist management"
    if "votemap" in endpoint or "vote_map" in endpoint:
        return "Vote map"
    if any(
        part in endpoint
        for part in (
            "map",
            "game_layout",
            "objective",
            "rotation",
            "match_timer",
            "warmup_timer",
        )
    ):
        return "Maps and rotations"
    if any(
        part in endpoint
        for part in (
            "player",
            "gamestate",
            "team_view",
            "slots",
            "status",
            "public_info",
            "game_mode",
            "get_name",
        )
    ):
        return "Players and server state"
    if any(
        part in endpoint for part in ("admin", "permission", "logged_in", "server_list")
    ):
        return "Admins and access"
    if any(part in endpoint for part in ("ban", "kick", "profanit")):
        return "Bans and profanity"
    if any(part in endpoint for part in ("message", "broadcast", "welcome")):
        return "Messages and templates"
    if any(part in endpoint for part in ("log", "audit", "history")):
        return "Logs and audit"
    if any(part in endpoint for part in ("score", "stats", "date_scoreboard")):
        return "Scoreboards and statistics"
    if any(part in endpoint for part in ("service", "webhook", "queue")):
        return "Services and automation"
    return "System and authentication"


def permissions_from_decorator(function: ast.FunctionDef | None) -> list[str]:
    if not function:
        return []
    call = decorator_call(function, "permission_required")
    if not call or not call.args:
        return []
    value = literal(call.args[0])
    if isinstance(value, str):
        return [value]
    return sorted(value) if isinstance(value, (list, tuple, set)) else []


def methods_from_decorator(function: ast.FunctionDef | None) -> list[str]:
    if not function:
        return ["POST"]
    call = decorator_call(function, "require_http_methods")
    if not call or not call.args:
        return ["POST"]
    value = literal(call.args[0])
    return list(value) if isinstance(value, (list, tuple)) else ["POST"]


def expression_type(node: ast.AST | None) -> str:
    if isinstance(node, ast.Dict):
        return "dict[str, Any]"
    if isinstance(node, (ast.List, ast.ListComp)):
        return "list[Any]"
    if isinstance(node, ast.Constant):
        return "None" if node.value is None else type(node.value).__name__
    if isinstance(node, ast.Call):
        name = dotted_name(node.func)
        if name.endswith(".model_json_schema") or name.endswith(".model_dump"):
            return "dict[str, Any]"
        if name in {"dict", "list", "bool", "int", "str", "float"}:
            return {"dict": "dict[str, Any]", "list": "list[Any]"}.get(name, name)
        if name.endswith(".load_from_db"):
            return name.rsplit(".", 2)[-2]
    return "Any"


def response_type(function: ast.FunctionDef | None) -> str:
    if not function:
        return "Any"
    if function.returns:
        annotation = ast.unparse(function.returns)
        if not any(part in annotation for part in ("HttpResponse", "RconJsonResponse")):
            return annotation

    annotations = {
        node.target.id: ast.unparse(node.annotation)
        for node in ast.walk(function)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assignments: dict[str, str] = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            candidate = expression_type(node.value)
            if candidate != "Any":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = candidate
    inferred = "Any"
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or not dotted_name(node.func).endswith(
            "api_response"
        ):
            continue
        result_keyword = next(
            (item for item in node.keywords if item.arg == "result"), None
        )
        if not result_keyword:
            continue
        value = result_keyword.value
        if isinstance(value, ast.Name) and value.id in annotations:
            return annotations[value.id]
        if isinstance(value, ast.Name) and value.id in assignments:
            inferred = assignments[value.id]
            continue
        candidate = expression_type(value)
        if candidate != "Any":
            inferred = candidate
    return inferred


def endpoint_response_type(endpoint: str, function: ast.FunctionDef | None) -> str:
    if endpoint.startswith("describe_"):
        return "dict[str, Any]"
    return RESPONSE_TYPE_OVERRIDES.get(endpoint, response_type(function))


def config_request_type(endpoint: str, plain: dict[str, ast.FunctionDef]) -> str | None:
    if not endpoint.endswith("_config") or not endpoint.startswith(
        ("set_", "validate_")
    ):
        return None
    stem = endpoint.removeprefix("set_").removeprefix("validate_")
    getter_name = f"get_{stem}"
    candidate = endpoint_response_type(getter_name, plain.get(getter_name))
    return candidate if candidate != "Any" else None


def has_decorator(function: ast.FunctionDef | None, name: str) -> bool:
    if not function:
        return False
    return any(
        dotted_name(item.func if isinstance(item, ast.Call) else item).endswith(name)
        for item in function.decorator_list
    )


def make_endpoint(
    name: str,
    function: ast.FunctionDef | None,
    methods: list[str],
    permissions: list[str],
    games: list[str],
    *,
    endpoint_id: str | None = None,
    always_authenticated: bool = False,
    request_type: str | None = None,
) -> dict[str, Any]:
    authenticated = (
        always_authenticated
        or has_decorator(function, "login_required")
        or bool(permissions)
    )
    parameters = function_parameters(function) if function else []
    required_overrides = {
        "login": {"username", "password"},
        "do_service": {"action", "service_name"},
        "set_auto_settings": {"settings"},
    }
    for parameter in parameters:
        if parameter["name"] in required_overrides.get(name, set()):
            parameter["required"] = True
            parameter["default"] = None

    return {
        "id": endpoint_id or name,
        "name": name,
        "title": endpoint_title(name),
        "path": f"/api/{name}",
        "methods": methods,
        "games": games,
        "category": category(name),
        "summary": clean_doc(function, name),
        "authenticated": authenticated,
        "permissions": permissions,
        "parameters": parameters,
        "requestType": request_type,
        "responseType": endpoint_response_type(name, function),
    }


def generate_endpoints() -> list[dict[str, Any]]:
    plain, class_methods = all_functions()
    views_tree = source_tree(API_DIR / "views.py")
    permissions = endpoint_dict(views_tree, "ENDPOINT_PERMISSIONS")
    methods = endpoint_dict(views_tree, "RCON_ENDPOINT_HTTP_METHODS")

    records: list[dict[str, Any]] = []
    for name in sorted(permissions):
        raw_permissions = permissions[name]
        permission_list = (
            [raw_permissions]
            if isinstance(raw_permissions, str)
            else sorted(raw_permissions)
        )
        records.append(
            make_endpoint(
                name,
                plain.get(name),
                list(methods.get(name, ["POST"])),
                permission_list,
                ["hll", "hllv"],
                always_authenticated=True,
                request_type=config_request_type(name, plain),
            )
        )

    game_definitions = {
        "hll": {
            "get_objective_rows": ("GET", "api.can_view_current_map", "HLLRcon"),
            "set_game_layout": ("POST", "api.can_change_game_layout", "HLLRcon"),
        },
        "hllv": {
            "get_objective_rows": ("GET", "api.can_view_current_map", "HLLVRcon"),
            "get_game_layouts": ("GET", "api.can_view_current_map", "HLLVRcon"),
            "get_game_layout": ("GET", "api.can_view_current_map", "HLLVRcon"),
            "set_game_layout": ("POST", "api.can_change_game_layout", "HLLVRcon"),
            "remove_game_layout": ("POST", "api.can_change_game_layout", "HLLVRcon"),
        },
    }
    for game, endpoints in game_definitions.items():
        for name, (method, permission, class_name) in endpoints.items():
            function = class_methods.get((class_name, name)) or plain.get(name)
            records.append(
                make_endpoint(
                    name,
                    function,
                    [method],
                    [permission],
                    [game],
                    endpoint_id=f"{name}-{game}",
                    always_authenticated=True,
                    request_type=config_request_type(name, plain),
                )
            )

    urls_source = (API_DIR / "urls.py").read_text(encoding="utf-8")
    explicit = re.findall(
        r'\(\s*"([a-zA-Z0-9_]+)"\s*,\s*([a-zA-Z0-9_.]+)\s*,?\s*\)',
        urls_source,
    )
    manual_names: set[str] = set()
    for name, reference in explicit:
        if name in manual_names:
            continue
        manual_names.add(name)
        function = plain.get(reference.rsplit(".", 1)[-1]) or plain.get(name)
        records.append(
            make_endpoint(
                name,
                function,
                methods_from_decorator(function),
                permissions_from_decorator(function),
                ["hll", "hllv"],
                request_type=config_request_type(name, plain),
            )
        )

    for name in (
        "get_version",
        "get_connection_info",
        "get_public_info",
        "run_raw_command",
        "get_system_usage",
    ):
        if name not in manual_names:
            function = plain[name]
            records.append(
                make_endpoint(
                    name,
                    function,
                    methods_from_decorator(function),
                    permissions_from_decorator(function),
                    ["hll", "hllv"],
                    request_type=config_request_type(name, plain),
                )
            )

    records.append(
        {
            "id": "get_api_documentation",
            "name": "get_api_documentation",
            "title": endpoint_title("get_api_documentation"),
            "path": "/api/get_api_documentation",
            "methods": ["GET", "POST"],
            "games": ["hll", "hllv"],
            "category": "System and authentication",
            "summary": "Return the live server's introspected route names, arguments, permissions, methods, and return annotations.",
            "authenticated": False,
            "permissions": [],
            "parameters": [],
            "requestType": None,
            "responseType": "list[ApiEndpointMetadata]",
        }
    )
    category_rank = {name: index for index, name in enumerate(CATEGORY_ORDER)}
    return sorted(
        records,
        key=lambda item: (
            category_rank[item["category"]],
            item["title"].lower(),
            item["id"],
        ),
    )


def class_kind(
    node: ast.ClassDef, known_kinds: dict[str, str] | None = None
) -> str | None:
    bases = {dotted_name(base).split("[")[0] for base in node.bases}
    base_names = {base.rsplit(".", 1)[-1] for base in bases}
    known_kinds = known_kinds or {}
    inherited = {known_kinds.get(base) for base in base_names}
    if "TypedDict" in base_names or "TypedDict" in inherited:
        return "TypedDict"
    if (
        "BaseModel" in base_names
        or "Pydantic model" in inherited
        or any(base.endswith("UserConfig") for base in base_names)
    ):
        return "Pydantic model"
    if "Enum" in " ".join(bases) or "enum.Enum" in bases or "enum.StrEnum" in bases:
        return "Enum"
    return None


def generate_schemas() -> list[dict[str, Any]]:
    schemas: list[dict[str, Any]] = [
        {
            "name": "ApiResponse",
            "kind": "Response envelope",
            "description": "The JSON envelope returned by CRCON endpoints.",
            "fields": [
                {"name": "result", "type": "T | null", "required": True},
                {"name": "command", "type": "string | null", "required": True},
                {"name": "arguments", "type": "object | null", "required": True},
                {"name": "failed", "type": "boolean", "required": True},
                {"name": "error", "type": "string | object | null", "required": True},
                {"name": "forward_results", "type": "object | null", "required": True},
                {"name": "version", "type": "string", "required": True},
            ],
        }
    ]
    paths = [
        ROOT / "rcon" / "types.py",
        ROOT / "rcon" / "maps.py",
        API_DIR / "log_stream.py",
        *sorted((ROOT / "rcon" / "user_config").glob("*.py")),
    ]
    class_nodes: list[ast.ClassDef] = []
    for path in paths:
        class_nodes.extend(
            node for node in source_tree(path).body if isinstance(node, ast.ClassDef)
        )

    known_kinds: dict[str, str] = {}
    pending = list(class_nodes)
    while pending:
        progress = False
        for node in list(pending):
            kind = class_kind(node, known_kinds)
            if kind:
                known_kinds[node.name] = kind
                pending.remove(node)
                progress = True
        if not progress:
            break

    seen = {"ApiResponse"}
    for node in class_nodes:
        if node.name in seen:
            continue
        kind = known_kinds.get(node.name)
        if not kind:
            continue
        fields: list[dict[str, Any]] = []
        if kind != "Enum":
            schema_lookup = {schema["name"]: schema for schema in schemas}
            for base in node.bases:
                base_name = dotted_name(base).rsplit(".", 1)[-1]
                if base_name in schema_lookup:
                    fields.extend(schema_lookup[base_name]["fields"])
        if kind == "Enum":
            for child in node.body:
                if (
                    isinstance(child, ast.Assign)
                    and len(child.targets) == 1
                    and isinstance(child.targets[0], ast.Name)
                ):
                    fields.append(
                        {
                            "name": child.targets[0].id,
                            "type": repr(literal(child.value)),
                            "required": True,
                        }
                    )
        else:
            total = not any(
                keyword.arg == "total" and literal(keyword.value) is False
                for keyword in node.keywords
            )
            for child in node.body:
                if not isinstance(child, ast.AnnAssign) or not isinstance(
                    child.target, ast.Name
                ):
                    continue
                annotation = ast.unparse(child.annotation)
                if kind == "Pydantic model":
                    required = child.value is None
                else:
                    required = total and not annotation.startswith("NotRequired[")
                fields.append(
                    {
                        "name": child.target.id,
                        "type": annotation,
                        "required": required,
                    }
                )
        if fields:
            schemas.append(
                {
                    "name": node.name,
                    "kind": kind,
                    "description": re.sub(
                        r"\s+", " ", ast.get_docstring(node) or ""
                    ).strip(),
                    "fields": fields,
                }
            )
            seen.add(node.name)
    return sorted(schemas, key=lambda item: item["name"].lower())


def main() -> None:
    endpoints = generate_endpoints()
    for game in ("hll", "hllv"):
        game_ids = [item["id"] for item in endpoints if game in item["games"]]
        if len(game_ids) != len(set(game_ids)):
            raise ValueError(f"Duplicate endpoint IDs generated for {game}")

    payload = {
        "generatedFrom": "rconweb/api and rcon controllers",
        "endpoints": endpoints,
        "schemas": generate_schemas(),
    }
    OUTPUT.write_text(
        "// Generated by scripts/generate_api_docs.py. Do not edit by hand.\n"
        f"window.CRCON_DOCS = {json.dumps(payload, indent=2, sort_keys=False)};\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {len(payload['endpoints'])} endpoints and {len(payload['schemas'])} schemas to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
