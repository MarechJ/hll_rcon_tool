from unittest import mock

import pydantic
import pytest
from pydantic import HttpUrl

import rcon.message_variables
from rcon.hooks import trigger_words
from rcon.message_variables import format_message_string, populate_message_variables
from rcon.types import (
    MessageVariable,
    MessageVariableContext,
    MostRecentEvents,
    StructuredLogLineType,
)
from rcon.user_config.trigger_words import TriggerWord, TriggerWordsUserConfig
from rcon.utils import contains_triggering_word


class MockRconServerSettingsUserConfig:
    def __init__(
        self, short_name="", discord_invite_url=HttpUrl("http://example.com")
    ) -> None:
        self.short_name = short_name
        self.discord_invite_url = discord_invite_url


class MockAdminPingWebhooksUserConfig:
    def __init__(self, trigger_words: list[str]) -> None:
        self.trigger_words = trigger_words


class MockTriggerWord:
    def __init__(self, words: list[str], message: str) -> None:
        self.words = words
        self.message = message


class MockTriggerWordsUserConfig:
    def __init__(
        self, enabled=True, trigger_words: list[TriggerWord] | None = None
    ) -> None:
        self.enabled = enabled
        self.trigger_words = trigger_words if trigger_words else []


def make_mock_stat(player: str, steam_id_64: str, *args, **kwargs):
    return {
        "player": player,
        "steam_id_64": steam_id_64,
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


@pytest.mark.parametrize("map_name, expected", [("carentan_warfare", "Carentan")])
def test_populate_next_map(monkeypatch, map_name, expected):
    var = MessageVariable.next_map
    monkeypatch.setattr(
        rcon.message_variables.Rcon, "get_gamestate", lambda x: {"next_map": map_name}
    )
    assert populate_message_variables([var.value]).get(var) == expected


@pytest.mark.parametrize(
    "rot, expected",
    [(["carentan_warfare", "utahbeach_warfare"], "Carentan, Utah")],
)
def test_populate_map_rotation(monkeypatch, rot, expected):
    var = MessageVariable.map_rotation
    monkeypatch.setattr(rcon.message_variables.Rcon, "get_map_rotation", lambda x: rot)
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
    "trigger_word, steam_id_64, recent_event, expected_message",
    [
        (
            TriggerWord(
                words=["!wkm"],
                message="You were last killed by {last_nemesis_name} with {last_nemesis_weapon}",
            ),
            "1234",
            MostRecentEvents(
                last_nemesis_name="some guy", last_nemesis_weapon="some weapon"
            ),
            "You were last killed by some guy with some weapon",
        ),
        (
            TriggerWord(
                words=["!lastkill"],
                message="Your last kill was {last_victim_name} with {last_victim_weapon}",
            ),
            "1234",
            MostRecentEvents(
                last_victim_name="some guy", last_victim_weapon="some weapon"
            ),
            "Your last kill was some guy with some weapon",
        ),
    ],
)
def test_trigger_words_hook(
    monkeypatch,
    # test_format_str: list[str],
    # test_words: str,
    trigger_word: TriggerWord,
    steam_id_64: str,
    recent_event: MostRecentEvents,
    expected_message: str,
):
    monkeypatch.setattr(
        rcon.hooks.TriggerWordsUserConfig,
        "load_from_db",
        lambda: MockTriggerWordsUserConfig(trigger_words=[trigger_word]),
    )
    monkeypatch.setattr(
        rcon.hooks,
        "get_recent_actions",
        lambda x: {steam_id_64: recent_event},
    )

    struct_log: StructuredLogLineType = {
        "action": "",
        "player": None,
        "steam_id_64_1": steam_id_64,
        "player2": None,
        "steam_id_64_2": None,
        "weapon": None,
        "message": "",
        "sub_content": trigger_word.words[0],
    }

    with mock.patch("rcon.hooks.Rcon") as rcon_:
        trigger_words(rcon_, struct_log)
        rcon_.do_message_player.assert_called_with(
            steam_id_64=steam_id_64,
            message=expected_message,
            save_message=False,
        )


@pytest.mark.parametrize(
    "chat_message, trigger_words, expected",
    [
        ("this contains a matching word", {"matching"}, True),
        ("this contains a matching word", {"zebra"}, False),
    ],
)
def test_contains_triggering_word(chat_message, trigger_words, expected):
    assert contains_triggering_word(chat_message, trigger_words) == expected


@pytest.mark.parametrize(
    "format_str, context, expected",
    [("{player_name}", {MessageVariableContext.player_name: "test_name"}, "test_name")],
)
def test_message_formatting(format_str, context, expected):
    assert format_message_string(format_str, context) == expected


@pytest.mark.parametrize("message", [("{unknown}")])
def test_invalid_message_variable_raises(message):
    with pytest.raises(pydantic.ValidationError):
        TriggerWordsUserConfig(
            trigger_words=[TriggerWord(message=message)],
        )


@pytest.mark.parametrize("message", [("{vip_expiration}")])
def test_valid_message_variable_does_not_raise(message):
    TriggerWordsUserConfig(
        trigger_words=[TriggerWord(message=message)],
    )
