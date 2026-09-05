from types import SimpleNamespace

import pytest
from pydantic import HttpUrl, ValidationError

from rcon import discord
from rcon.user_config.webhooks import AuditDiscordWebhook, AuditWebhooksUserConfig


def test_audit_webhook_config_supports_optional_thread_id():
    config = AuditWebhooksUserConfig(
        hooks=[
            AuditDiscordWebhook(
                url=HttpUrl("https://discord.com/api/webhooks/1/token"),
                thread_id="123456789012345678",
            ),
            AuditDiscordWebhook(
                url=HttpUrl("https://discord.com/api/webhooks/2/token"),
            ),
        ]
    )

    assert config.hooks[0].thread_id == "123456789012345678"
    assert config.hooks[1].thread_id is None


def test_audit_webhook_config_rejects_non_numeric_thread_id():
    with pytest.raises(ValidationError):
        AuditDiscordWebhook(
            url=HttpUrl("https://discord.com/api/webhooks/1/token"),
            thread_id="not-a-thread-id",
        )


def test_audit_delivery_passes_configured_thread_id(monkeypatch):
    created_hooks = []
    queued_messages = []

    class FakeWebhook:
        def __init__(self, **kwargs):
            created_hooks.append(kwargs)
            self.json = {
                **kwargs,
                "webhook_id": "1",
                "rate_limit_retry": False,
            }

    config = AuditWebhooksUserConfig(
        hooks=[
            AuditDiscordWebhook(
                url=HttpUrl("https://discord.com/api/webhooks/1/token"),
                thread_id="123456789012345678",
            )
        ]
    )
    monkeypatch.setattr(
        discord.AuditWebhooksUserConfig,
        "load_from_db",
        lambda: config,
    )
    monkeypatch.setattr(
        discord.RconServerSettingsUserConfig,
        "load_from_db",
        lambda: SimpleNamespace(short_name="TEST"),
    )
    monkeypatch.setattr(discord, "get_server_number", lambda: 1)
    monkeypatch.setattr(discord, "DiscordWebhook", FakeWebhook)
    monkeypatch.setattr(
        discord,
        "enqueue_message",
        lambda *, message: queued_messages.append(message),
    )

    discord.send_to_discord_audit("changed settings", "test_command")

    assert created_hooks[0]["thread_id"] == "123456789012345678"
    assert queued_messages[0].payload["thread_id"] == "123456789012345678"
