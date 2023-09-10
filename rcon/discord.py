import logging
import os
import re
from functools import lru_cache
from typing import List

import requests
from discord_webhook import DiscordWebhook

from discord import RequestsWebhookAdapter, Webhook
from rcon.user_config.webhooks import (
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


def make_hook(webhook_url):
    webhook_id, webhook_token = parse_webhook_url(webhook_url)
    if not all([webhook_id, webhook_token]):
        return None
    return Webhook.partial(
        id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
    )


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


def get_prepared_discord_hooks(hook_type: str) -> List[DiscordWebhook]:
    if hook_type == CameraWebhooksUserConfig.KEY_NAME:
        hooks = CameraWebhooksUserConfig.load_from_db().hooks
    elif hook_type == WatchlistWebhooksUserConfig.KEY_NAME:
        hooks = WatchlistWebhooksUserConfig.load_from_db().hooks
    else:
        raise ValueError(f"{hook_type} is not a valid webhook type")

    return [
        DiscordWebhook(
            url=hook.url,
            allowed_mentions=make_allowed_mentions(
                hook.user_mentions, hook.role_mentions
            ),
            content=" ".join(
                [v.value for v in hook.user_mentions]
                + [v.value for v in hook.role_mentions]
            ),
        )
        for hook in hooks
    ]


def dict_to_discord(d):
    return "   ".join([f"{k}: `{v}`" for k, v in d.items()])


def send_to_discord_audit(message, by=None, silent=True, webhookurl=None):
    webhookurl = webhookurl or os.getenv("DISCORD_WEBHOOK_AUDIT_LOG", None)
    # Flatten messages with newlines
    message = message.replace("\n", " ")
    logger.info("Audit: [%s] %s", by, message)
    if not webhookurl:
        logger.debug("No webhook set for audit log")
        return
    try:
        server_name = os.getenv(
            "SERVER_SHORT_NAME", os.getenv("SERVER_SHORT_NAME", "Undefined")
        )
        webhook = DiscordWebhook(
            url=webhookurl, content="[{}][**{}**] {}".format(server_name, by, message)
        )
        return webhook.execute()
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise
