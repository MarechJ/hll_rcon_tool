import logging
import os
import re
from typing import List

from discord_webhook import DiscordWebhook

from rcon.user_config import DiscordHookConfig

logger = logging.getLogger(__name__)


def make_allowed_mentions(roles):
    allowed_mentions = {}
    for r in roles:
        if match := re.match(r"<@\!(\d+)>", r):
            allowed_mentions.setdefault("users", []).append(match.group(1))
        if match := re.match(r"<@&(\d+)>", r):
            allowed_mentions.setdefault("roles", []).append(match.group(1))
        if r == "@everyone" or r == "@here":
            allowed_mentions["parse"] = r.replace("@", "")
    print(allowed_mentions)
    # allowed_mentions = {"parse": ["users"]}
    return allowed_mentions


def get_prepared_discord_hooks(type) -> List[DiscordWebhook]:
    config = DiscordHookConfig(type)
    hooks = config.get_hooks()

    return [
        DiscordWebhook(
            url=hook.hook,
            allowed_mentions=make_allowed_mentions(hook.roles),
            content=" ".join(hook.roles),
        )
        for hook in hooks.hooks
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
