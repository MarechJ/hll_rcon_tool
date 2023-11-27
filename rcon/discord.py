import logging
import re
from functools import lru_cache
from typing import List, Type

import requests
from discord_webhook import DiscordWebhook
from pydantic import HttpUrl

from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import (
    AuditWebhooksUserConfig,
    BaseMentionWebhookUserConfig,
    BaseWebhookUserConfig,
    CameraWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
)


@lru_cache
def parse_webhook_url(url):
    """Parse and check validity of Discord webhook URL
    by performing a get request and checking existence
    of 'id' and 'token' in the JSON response.
    """
    if not url:
        return None, None
    resp = requests.get(url, timeout=10).json()
    _id = int(resp["id"])
    token = resp["token"]
    return _id, token


logger = logging.getLogger(__name__)


def make_hook(webhook_url) -> DiscordWebhook | None:
    webhook_id, webhook_token = parse_webhook_url(webhook_url)
    if not all([webhook_id, webhook_token]):
        return None

    return DiscordWebhook(url=webhook_url)


def make_allowed_mentions(user_ids, role_ids):
    allowed_mentions = {}
    for r in user_ids + role_ids:
        if match := re.match(r"<@\!(\d+)>", r):
            allowed_mentions.setdefault("users", []).append(match.group(1))
        if match := re.match(r"<@&(\d+)>", r):
            allowed_mentions.setdefault("roles", []).append(match.group(1))
        if r == "@everyone" or r == "@here":
            allowed_mentions["parse"] = r.replace("@", "")
    print(allowed_mentions)
    # allowed_mentions = {"parse": ["users"]}
    return allowed_mentions


def get_prepared_discord_hooks(
    hook_type: Type[CameraWebhooksUserConfig | WatchlistWebhooksUserConfig],
) -> List[DiscordWebhook]:
    hooks = hook_type.load_from_db().hooks

    return [
        DiscordWebhook(
            url=str(hook.url),
            allowed_mentions=make_allowed_mentions(
                hook.user_mentions, hook.role_mentions
            ),
            content=" ".join(
                [v for v in hook.user_mentions] + [v for v in hook.role_mentions]
            ),
        )
        for hook in hooks
    ]


def dict_to_discord(d):
    return "   ".join([f"{k}: `{v}`" for k, v in d.items()])


def send_to_discord_audit(
    message, by=None, silent=True, webhookurls: list[HttpUrl | None] | None = None
):
    config = None

    if webhookurls is None:
        config = AuditWebhooksUserConfig.load_from_db()
        webhookurls = [hook.url for hook in config.hooks]

    server_config = RconServerSettingsUserConfig.load_from_db()

    # Flatten messages with newlines
    message = message.replace("\n", " ")
    logger.info("Audit: [%s] %s", by, message)
    if not webhookurls:
        logger.debug("No webhooks set for audit log")
        return
    try:
        dh_webhooks = [
            DiscordWebhook(
                url=str(url),
                content="[{}][**{}**] {}".format(server_config.short_name, by, message),
            )
            for url in webhookurls
            if url
        ]

        responses = [hook.execute() for hook in dh_webhooks]
        return responses
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise
