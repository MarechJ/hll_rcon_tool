import logging
import re
from functools import lru_cache
from typing import Any, List, Type

import requests
from discord_webhook import DiscordWebhook
from pydantic import HttpUrl

from discord.utils import escape_markdown
from rcon.discord_asyncio import DiscordAsyncio
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.utils import (
    DISCORD_AUDIT_FORMAT,
    BaseUserConfig,
    mask_sensitive_data,
)
from rcon.user_config.webhooks import (
    AuditWebhooksUserConfig,
    CameraWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
)
from rcon.utils import dict_differences


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


def audit_user_config_differences(
    old_model: dict[str, Any] | BaseUserConfig,
    new_model: dict[str, Any] | BaseUserConfig,
    command_name,
    author,
):
    if isinstance(old_model, BaseUserConfig):
        old_model = old_model.model_dump()
    if isinstance(new_model, BaseUserConfig):
        new_model = new_model.model_dump()

    differences = dict_differences(old_model, new_model)
    mask_sensitive_data(differences)
    message = DISCORD_AUDIT_FORMAT.format(differences=str(differences))
    send_to_discord_audit(
        message=message,
        command_name=command_name,
        by=author,
        md_escape_message=False,
    )


def send_to_discord_audit(
    message: str,
    command_name: str,
    by: str | None = None,
    silent=True,
    webhookurls: list[HttpUrl | None] | None = None,
    md_escape_message: bool = True,
    md_escape_author: bool = True,
):
    by = by or "CRCON"
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
        content = "[`{}`][`{}`]][**{}**] {}".format(
            server_config.short_name,
            command_name,
            escape_markdown(by) if md_escape_author else by,
            escape_markdown(message) if md_escape_message else message,
        )
        logger.info(f"send_to_discord_audit {content=}")
        # TODO: fix typing or set `by` to something besides None
        dh_webhooks = [
            DiscordWebhook(
                url=str(url),
                content=content,
            )
            for url in webhookurls
            if url
        ]

        # use DiscordAsyncio to send webhooks asynchronously
        # we get a future, not a response, but i don't see code using the responses
        for hook in dh_webhooks:
            DiscordAsyncio().send_webhook(hook)
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise
