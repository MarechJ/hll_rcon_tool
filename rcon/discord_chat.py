import logging
import os
from urllib.parse import urlparse

import discord.utils
from discord import RequestsWebhookAdapter
from discord import Webhook

from rcon.game_logs import on_chat

DISCORD_CHAT_WEBHOOK_URL = os.getenv("DISCORD_CHAT_WEBHOOK")
WEBHOOK_ID = None
WEBHOOK_TOKEN = None

logger = logging.getLogger(__name__)


def post_chat_message_to_discord(_, log):
    try:
        message = log["message"]
        message = discord.utils.escape_mentions(message)
        message = discord.utils.escape_markdown(message)

        webhook = Webhook.partial(
            id=WEBHOOK_ID, token=WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter()
        )
        webhook.send(message)

    except Exception as e:
        logger.error("error executing chat message webhook: %s", e)


def parse_webhook_url(url):
    try:
        parsed = urlparse(url)
        path = parsed.path.split("/")
        token = path[-1]
        _id = int(path[-2])
        return _id, token
    except Exception as e:
        logger.error("error parsing Discord chat webhook url: %s", e)


# Only parse ID and token and apply decorator if webhook URL was provided.
if DISCORD_CHAT_WEBHOOK_URL:
    WEBHOOK_ID, WEBHOOK_TOKEN = parse_webhook_url(DISCORD_CHAT_WEBHOOK_URL)
    post_chat_message_to_discord = on_chat(post_chat_message_to_discord)
