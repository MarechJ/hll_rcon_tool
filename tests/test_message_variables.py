from datetime import datetime
from logging import getLogger
from unittest import mock

import pydantic
import pytest
from pydantic import HttpUrl

import rcon.message_variables
from rcon.hooks import chat_commands
from rcon.maps import parse_layer
from rcon.message_variables import (
    format_message_string,
    format_winning_map,
    populate_message_variables,
)
from rcon.types import (
    MessageVariable,
    MessageVariableContext,
    MostRecentEvents,
    StructuredLogLineWithMetaData,
)
from rcon.user_config.chat_commands import (
    ChatCommand,
    ChatCommandsUserConfig,
    chat_contains_command_word,
    is_command_word,
    is_description_word,
    is_help_word,
)

logger = getLogger(__name__)


class MockRconServerSettingsUserConfig:
    def __init__(
        self, short_name="", discord_invite_url=HttpUrl("http://example.com")
    ) -> None:
        self.short_name = short_name
        self.discord_invite_url = discord_invite_url


class MockAdminPingWebhooksUserConfig:
    def __init__(self, trigger_words: list[str]) -> None:
        self.trigger_words = trigger_words


def make_mock_stat(player: str, player_id: str, *args, **kwargs):
    return {
        "player": player,
        "player_id": player_id,
        **kwargs,
    }


test_populate_top_kills_stats = {
    "stats": [
        make_mock_stat("test1", "1", kills=1),
        make_mock_stat("test2", "2", kills=2),
        make_mock_stat("test3", "3", kills=3),
        make_mock_stat("test4", "4", kills=3),
    ]
}

test_populate_top_kill_streaks_stats = {
    "stats": [
        make_mock_stat("test1", "1", kills_streak=1),
        make_mock_stat("test2", "2", kills_streak=2),
        make_mock_stat("test3", "3", kills_streak=3),
        make_mock_stat("test4", "4", kills_streak=3),
    ]
}


def test_populate_server_name(monkeypatch):
    server_name = "Some Sample Name"
    var = MessageVariable.server_name
    monkeypatch.setattr(rcon.message_variables.Rcon, "get_name", lambda x: server_name)

    assert populate_message_variables([var.value]).get(var) == server_name


def test_populate_server_short_name(monkeypatch):
    name = "Some short name"
    var = MessageVariable.server_short_name
    monkeypatch.setattr(
        rcon.message_variables.RconServerSettingsUserConfig,
        "load_from_db",
        lambda: MockRconServerSettingsUserConfig(short_name=name),
    )
    assert populate_message_variables([var.value]).get(var) == name


@pytest.mark.parametrize(
    "url, expected", [(HttpUrl("http://example.com/"), "http://example.com/")]
)
def test_populate_discord_invite_url(monkeypatch, url, expected):
    var = MessageVariable.discord_invite_url
    monkeypatch.setattr(
        rcon.message_variables.RconServerSettingsUserConfig,
        "load_from_db",
        lambda: MockRconServerSettingsUserConfig(discord_invite_url=url),
    )
    assert populate_message_variables([var.value]).get(var) == expected


def test_populate_admin_ping_trigger_words(monkeypatch):
    trigger_words = ["!admin", "!help", "help"]
    var = MessageVariable.admin_ping_trigger_words
    monkeypatch.setattr(
        rcon.message_variables.AdminPingWebhooksUserConfig,
        "load_from_db",
        lambda: MockAdminPingWebhooksUserConfig(trigger_words=trigger_words),
    )
    assert populate_message_variables([var.value]).get(var) == ", ".join(trigger_words)


@pytest.mark.parametrize("mods, expected", [(["1", "2", "3"], "3"), ([], "0")])
def test_populate_num_online_mods(monkeypatch, mods, expected):
    var = MessageVariable.num_online_mods
    monkeypatch.setattr(rcon.message_variables, "online_mods", lambda: mods)
    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize("mods, expected", [(["1", "2", "3"], "3"), ([], "0")])
def test_populate_num_ingame_mods(monkeypatch, mods, expected):
    var = MessageVariable.num_ingame_mods
    monkeypatch.setattr(rcon.message_variables, "ingame_mods", lambda: mods)
    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "map_name, expected", [("carentan_warfare", "Carentan Warfare")]
)
def test_populate_next_map(monkeypatch, map_name, expected):
    var = MessageVariable.next_map
    logger.error(f"{map_name=}")
    logger.error(f"{parse_layer(map_name)=}")
    monkeypatch.setattr(
        rcon.message_variables.Rcon,
        "get_next_map",
        lambda x: parse_layer(map_name),
    )
    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "rot, expected",
    [
        (
            ["carentan_warfare", "utahbeach_warfare"],
            "Carentan Warfare, Utah Beach Warfare",
        )
    ],
)
def test_populate_map_rotation(monkeypatch, rot, expected):
    var = MessageVariable.map_rotation
    monkeypatch.setattr(
        rcon.message_variables.Rcon,
        "get_map_rotation",
        lambda x: [parse_layer(m) for m in rot],
    )
    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "var, expected",
    [
        (MessageVariable.top_kills_player_name, "test3, test4"),
        (MessageVariable.top_kills_player_score, "3"),
    ],
)
def test_populate_top_kills(monkeypatch, var, expected):
    monkeypatch.setattr(
        rcon.message_variables,
        "get_cached_live_game_stats",
        lambda: test_populate_top_kills_stats,
    )

    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "var, expected",
    [
        (MessageVariable.top_kill_streak_player_name, "test3, test4"),
        (MessageVariable.top_kill_streak_player_score, "3"),
    ],
)
def test_populate_top_kill_streaks(monkeypatch, var, expected):
    monkeypatch.setattr(
        rcon.message_variables,
        "get_cached_live_game_stats",
        lambda: test_populate_top_kill_streaks_stats,
    )

    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "chat_content, config, player_id, recent_event, expected_message",
    [
        (
            "!wkm miscellaneous words",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                        description="",
                    )
                ],
                describe_words=["!help"],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "You were last killed by some guy with some weapon",
        ),
        (
            "in the @wkm middle",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["@wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                    )
                ],
                describe_words=[],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "You were last killed by some guy with some weapon",
        ),
        (
            "!wkm @wkm",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!wkm", "@wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                    ),
                ],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "You were last killed by some guy with some weapon",
        ),
        (
            "what was my !lastkill ?lastkill",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!lastkill"],
                        message="Your last kill was {last_victim_name} with {last_victim_weapon}",
                    ),
                ],
            ),
            "1234",
            MostRecentEvents(
                last_victim_name="some guy", last_victim_weapon="some weapon"
            ),
            "Your last kill was some guy with some weapon",
        ),
    ],
)
def test_chat_commands_hook_command_words(
    monkeypatch,
    chat_content: str,
    config: ChatCommandsUserConfig,
    player_id: str,
    recent_event: MostRecentEvents,
    expected_message: str,
):
    monkeypatch.setattr(
        rcon.hooks.ChatCommandsUserConfig,
        "load_from_db",
        lambda: config,
    )
    monkeypatch.setattr(
        rcon.hooks,
        "get_recent_actions",
        lambda: {player_id: recent_event},
    )

    struct_log: StructuredLogLineWithMetaData = {
        "version": 1,
        "timestamp_ms": int(datetime.now().timestamp()),
        "event_time": datetime.now(),
        "relative_time_ms": None,
        "line_without_time": "",
        "raw": "",
        "action": "",
        "player_name_1": None,
        "player_id_1": player_id,
        "player_name_2": None,
        "player_id_2": None,
        "weapon": None,
        "message": "",
        "sub_content": chat_content,
    }

    with mock.patch("rcon.hooks.Rcon") as rcon_:
        chat_commands(rcon_, struct_log)
        rcon_.message_player.assert_called_once_with(
            player_id=player_id,
            message=expected_message,
            save_message=False,
        )


@pytest.mark.parametrize(
    "chat_content, config, player_id, recent_event, expected_message",
    [
        (
            "?wkm miscellaneous words",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                        description="Who last killed me",
                    )
                ],
                describe_words=["!help"],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "Who last killed me",
        ),
        (
            "in the ?wkm middle",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["@wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                        description="Who last killed me",
                    )
                ],
                describe_words=[],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "Who last killed me",
        ),
        (
            "?wkm ?wkm",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!wkm", "@wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                        description="Who last killed me",
                    ),
                ],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "Who last killed me",
        ),
        (
            "what was my ?lastkill",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!lastkill"],
                        message="Your last kill was {last_victim_name} with {last_victim_weapon}",
                        description="Who last killed me",
                    ),
                ],
            ),
            "1234",
            MostRecentEvents(
                last_victim_name="some guy", last_victim_weapon="some weapon"
            ),
            "Who last killed me",
        ),
    ],
)
def test_chat_commands_hook_help_words(
    monkeypatch,
    chat_content: str,
    config: ChatCommandsUserConfig,
    player_id: str,
    recent_event: MostRecentEvents,
    expected_message: str,
):
    monkeypatch.setattr(
        rcon.hooks.ChatCommandsUserConfig,
        "load_from_db",
        lambda: config,
    )
    monkeypatch.setattr(
        rcon.hooks,
        "get_recent_actions",
        lambda: {player_id: recent_event},
    )

    struct_log: StructuredLogLineWithMetaData = {
        "version": 1,
        "timestamp_ms": int(datetime.now().timestamp()),
        "event_time": datetime.now(),
        "relative_time_ms": None,
        "line_without_time": "",
        "raw": "",
        "action": "",
        "player_name_1": None,
        "player_id_1": player_id,
        "player_name_2": None,
        "player_id_2": None,
        "weapon": None,
        "message": "",
        "sub_content": chat_content,
    }

    with mock.patch("rcon.hooks.Rcon") as rcon_:
        chat_commands(rcon_, struct_log)
        rcon_.message_player.assert_called_once_with(
            player_id=player_id,
            message=expected_message,
            save_message=False,
        )


@pytest.mark.parametrize(
    "chat_content, config, player_id, recent_event, expected_message",
    [
        (
            "!help",
            ChatCommandsUserConfig(
                enabled=True,
                command_words=[
                    ChatCommand(
                        words=["!wkm"],
                        message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
                        description="Who last killed me",
                    )
                ],
                describe_words=["!help"],
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "!wkm | Who last killed me",
        ),
    ],
)
def test_chat_commands_hook_description_words(
    monkeypatch,
    chat_content: str,
    config: ChatCommandsUserConfig,
    player_id: str,
    recent_event: MostRecentEvents,
    expected_message: str,
):
    monkeypatch.setattr(
        rcon.hooks.ChatCommandsUserConfig,
        "load_from_db",
        lambda: config,
    )
    monkeypatch.setattr(
        rcon.hooks,
        "get_recent_actions",
        lambda: {player_id: recent_event},
    )

    struct_log: StructuredLogLineWithMetaData = {
        "version": 1,
        "timestamp_ms": int(datetime.now().timestamp()),
        "event_time": datetime.now(),
        "relative_time_ms": None,
        "line_without_time": "",
        "raw": "",
        "action": "",
        "player_name_1": None,
        "player_id_1": player_id,
        "player_name_2": None,
        "player_id_2": None,
        "weapon": None,
        "message": "",
        "sub_content": chat_content,
    }

    with mock.patch("rcon.hooks.Rcon") as rcon_:
        chat_commands(rcon_, struct_log)
        rcon_.message_player.assert_called_once_with(
            player_id=player_id,
            message=expected_message,
            save_message=False,
        )


@pytest.mark.parametrize(
    "chat_message, trigger_words, expected",
    [
        ("this contains a matching word", {"matching"}, "matching"),
        ("this contains a matching word", {"zebra"}, None),
    ],
)
def test_chat_contains_command_word(chat_message, trigger_words, expected):
    assert (
        chat_contains_command_word(set(chat_message.split()), trigger_words, set())
        == expected
    )


@pytest.mark.parametrize(
    "format_str, context, expected",
    [("{player_name}", {MessageVariableContext.player_name: "test_name"}, "test_name")],
)
def test_message_formatting(format_str, context, expected):
    assert format_message_string(format_str, context) == expected


@pytest.mark.parametrize("message", [("{unknown}")])
def test_invalid_message_variable_raises(message):
    with pytest.raises(pydantic.ValidationError):
        ChatCommandsUserConfig(
            command_words=[ChatCommand(message=message)],
        )


@pytest.mark.parametrize("message", [("{vip_expiration}")])
def test_valid_message_variable_does_not_raise(message):
    ChatCommandsUserConfig(
        command_words=[ChatCommand(message=message)],
    )


@pytest.mark.parametrize(
    "word, expected", [("!yes", True), ("yes", False), ("", False)]
)
def test_is_command_word(word, expected):
    assert is_command_word(word) == expected


@pytest.mark.parametrize(
    "word, expected", [("!yes", False), ("yes", False), ("", False), ("?yes", True)]
)
def test_is_help(word, expected):
    assert is_help_word(word) == expected


@pytest.mark.parametrize(
    "words, description_words, expected",
    [
        ("some triggering sentence help me", ["help"], True),
        ("not containing a triggering word", ["zebra"], False),
    ],
)
def test_is_description_word(words, description_words, expected):
    assert is_description_word(set(words.split()), description_words) == expected


# @mock.patch("rcon.get_next_map", autospec=True, return_value="carentan_warfare")
@pytest.mark.parametrize(
    "winning_maps, expected",
    [
        ([(parse_layer("carentan_warfare"), 2)], "Carentan Warfare (2 vote(s))"),
        ([(parse_layer("driel_offensive_ger"), 2)], "Driel Off. GER (2 vote(s))"),
    ],
)
def test_format_winning_map(winning_maps, expected) -> None:
    with (
        mock.patch("rcon.game_logs.Rcon", autospec=True) as ctl,
        # mock.patch("rcon.get_next_map", return_value="carentan_warfare") as _,
    ):
        assert format_winning_map(ctl=ctl, winning_maps=winning_maps) == expected
