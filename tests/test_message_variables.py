import pytest
from pydantic import HttpUrl

import rcon.message_variables
from rcon.message_variables import format_message_string, populate_message_variables
from rcon.types import MessageVariable
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


def make_mock_stat(player: str, steam_id_64: str, *args, **kwargs):
    return {
        "player": player,
        "steam_id_64": steam_id_64,
        **kwargs,
    }


sample_stats = {
    "stats": [
        make_mock_stat("test1", "1", kills=1),
        make_mock_stat("test2", "2", kills=2),
        make_mock_stat("test3", "3", kills=3),
        make_mock_stat("test4", "4", kills=3),
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
        rcon.message_variables, "get_cached_live_game_stats", lambda: sample_stats
    )

    assert populate_message_variables([var.value]).get(var) == expected


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
    [("{player_name}", {MessageVariable.player_name: "test_name"}, "test_name")],
)
def test_message_formatting(format_str, context, expected):
    assert format_message_string(format_str, context) == expected
