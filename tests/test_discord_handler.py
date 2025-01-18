from pydantic import HttpUrl

from rcon.discord_chat import DiscordWebhookHandler
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    ChatWebhooksUserConfig,
    DiscordMentionWebhook,
    DiscordWebhook,
    KillsWebhooksUserConfig,
)


def test_no_mentions():
    config = ChatWebhooksUserConfig(
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
        allow_mentions=True,
    )
    handler = DiscordWebhookHandler(chat_wh_config=config)
    embed = handler.create_chat_message(
        log={
            "sub_content": "test message",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "test message"


def test_chat_mentions_are_escaped():
    config = ChatWebhooksUserConfig(
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
        allow_mentions=False,
    )
    handler = DiscordWebhookHandler(chat_wh_config=config)
    embed = handler.create_chat_message(
        log={
            "sub_content": "test message @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "test message @\u200bhere"


def test_admin_ping_mentions_always_escaped():
    handler = DiscordWebhookHandler()

    embed = handler.create_chat_embed(
        log={
            "sub_content": "test message @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        },
        allow_mentions=False,
    )

    assert embed.description == "test message @\u200bhere"


def test_mentions_are_not_escaped():
    config = ChatWebhooksUserConfig(
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
        allow_mentions=True,
    )
    # monkeypatch.setattr(DiscordWebhookHandler, "_make_hook", lambda: [])
    handler = DiscordWebhookHandler(chat_wh_config=config)
    embed = handler.create_chat_message(
        log={
            "sub_content": "test message @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "test message @here"


def test_admin_pings_mention_start():
    config = AdminPingWebhooksUserConfig(
        trigger_words=["!admin"],
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
    )

    handler = DiscordWebhookHandler(admin_wh_config=config)
    content, embed, triggered = handler.create_admin_ping_message(
        log={
            "sub_content": "!admin test @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "__**!admin**__ test @\u200bhere"
    assert triggered
    assert content == "<@1212>"


def test_admin_pings_mention_middle():
    config = AdminPingWebhooksUserConfig(
        trigger_words=["!admin"],
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
    )

    handler = DiscordWebhookHandler(admin_wh_config=config)
    content, embed, triggered = handler.create_admin_ping_message(
        log={
            "sub_content": "test !admin @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "test __**!admin**__ @\u200bhere"
    assert content == "<@1212>"
    assert triggered


def test_admin_pings_contains_numbers():
    config = AdminPingWebhooksUserConfig(
        trigger_words=["testword123"],
        hooks=[
            DiscordMentionWebhook(
                url=HttpUrl("http://example.com"),
                user_mentions=["<@1212>"],
                role_mentions=[],
            )
        ],
    )

    handler = DiscordWebhookHandler(admin_wh_config=config)
    content, embed, triggered = handler.create_admin_ping_message(
        log={
            "sub_content": "testword123 test @here",
            "player_name_1": "some dude",
            "player_id_1": "1234",
            "action": "CHAT[Allies][Team]",
        }
    )

    assert embed.description == "__**testword123**__ test @\u200bhere"
    assert triggered
    assert content == "<@1212>"


def test_kill_message():
    config = KillsWebhooksUserConfig(
        send_kills=True,
        send_team_kills=False,
        hooks=[DiscordWebhook(url=HttpUrl("http://example.com"))],
    )

    handler = DiscordWebhookHandler(kills_wh_config=config)

    embed = handler.create_kill_message(
        log={
            "action": "KILL",
            "player_name_1": "EL MONO LOKO",
            "player_id_1": "76561198823171234",
            "player_name_2": "zerothreeOG",
            "player_id_2": "76561199371581234",
            "weapon": "MG42",
        },
    )

    killer, victim, weapon = embed.fields

    assert killer["name"] == "Killer"
    assert killer["value"].startswith("[EL MONO LOKO]")  # type: ignore

    assert victim["name"] == "Victim"
    assert victim["value"].startswith("[zerothreeOG]")  # type: ignore

    assert weapon["name"] == "Weapon"
    assert weapon["value"] == "MG42"


def test_team_kill_message():
    config = KillsWebhooksUserConfig(
        send_kills=True,
        send_team_kills=False,
        hooks=[DiscordWebhook(url=HttpUrl("http://example.com"))],
    )

    handler = DiscordWebhookHandler(kills_wh_config=config)

    embed = handler.create_kill_message(
        log={
            "action": "TEAM KILL",
            "player_name_1": "EL MONO LOKO",
            "player_id_1": "76561198823171234",
            "player_name_2": "zerothreeOG",
            "player_id_2": "76561199371581234",
            "weapon": "MG42",
        },
    )

    killer, victim, weapon = embed.fields

    assert killer["name"] == "Team Killer"
    assert killer["value"].startswith("[EL MONO LOKO]")  # type: ignore

    assert victim["name"] == "Victim"
    assert victim["value"].startswith("[zerothreeOG]")  # type: ignore

    assert weapon["name"] == "Weapon"
    assert weapon["value"] == "MG42"
