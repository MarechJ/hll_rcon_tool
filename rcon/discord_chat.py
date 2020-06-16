import logging
import os
from functools import lru_cache

import discord.utils
import requests
from discord import RequestsWebhookAdapter
from discord import Webhook

from rcon.game_logs import on_chat

DISCORD_CHAT_WEBHOOK_URL = os.getenv("DISCORD_CHAT_WEBHOOK")

logger = logging.getLogger(__name__)


@on_chat
def post_chat_message_to_discord(_, log):
    webhook_id, webhook_token = parse_webhook_url(DISCORD_CHAT_WEBHOOK_URL)
    if not all([webhook_id, webhook_token]):
        return

    try:
        message = f"{log['action']}: {log['message']}"
        message = discord.utils.escape_mentions(message)
        message = discord.utils.escape_markdown(message)

        webhook = Webhook.partial(
            id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
        )
        logger.info("sending chat message len=%s to Discord", len(message))
        webhook.send(message)

    except Exception as e:
        logger.error("error executing chat message webhook: %s", e)


@lru_cache
def parse_webhook_url(url):
    """Parse and check validity of Discord webhook URL
    by performing a get request and checking existence
    of 'id' and 'token' in the JSON response.
    """
    if not url:
        logger.info("no Discord chat webhook URL provided")
        return None, None

    try:
        resp = requests.get(url).json()
        _id = int(resp["id"])
        token = resp["token"]
        return _id, token
    except Exception as e:
        logger.error("error parsing Discord chat webhook url: %s", e)
        return None, None
