from rcon.logs import loop
from rcon.user_config import log_line_webhooks
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig


def test_log_line_config_preserves_thread_id(monkeypatch):
    saved = []
    monkeypatch.setattr(
        log_line_webhooks,
        "set_user_config",
        lambda name, config: saved.append(config),
    )

    LogLineWebhookUserConfig.save_to_db(
        {
            "webhooks": [
                {
                    "log_types": ["CHAT"],
                    "webhook": {
                        "url": "https://discord.com/api/webhooks/1/token",
                        "thread_id": "123456789012345678",
                        "user_mentions": [],
                        "role_mentions": [],
                    },
                }
            ]
        }
    )

    assert saved[0].webhooks[0].webhook.thread_id == "123456789012345678"


def test_log_line_delivery_passes_thread_id(monkeypatch):
    created_hooks = []
    webhook = log_line_webhooks.DiscordMentionWebhook(
        url="https://discord.com/api/webhooks/1/token",
        thread_id="123456789012345678",
        user_mentions=[],
        role_mentions=[],
    )

    class FakeHook:
        content = None
        allowed_mentions = None

        def add_embed(self, embed):
            pass

        def execute(self):
            pass

    monkeypatch.setattr(
        loop,
        "make_hook",
        lambda url, thread_id=None: (
            created_hooks.append((url, thread_id)) or FakeHook()
        ),
    )
    monkeypatch.setattr(
        loop.RconServerSettingsUserConfig,
        "load_from_db",
        lambda: type("Config", (), {"short_name": "TEST"})(),
    )

    loop.send_log_line_webhook_message(
        webhook,
        None,
        {
            "line_without_time": "CHAT test",
            "timestamp_ms": 0,
        },
    )

    assert created_hooks[0][1] == "123456789012345678"
