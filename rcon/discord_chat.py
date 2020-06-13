import logging
import os

import discord.utils
import requests
from discord import RequestsWebhookAdapter
from discord import Webhook

from rcon.game_logs import on_chat

DISCORD_CHAT_WEBHOOK_URL = os.getenv("DISCORD_CHAT_WEBHOOK")

logger = logging.getLogger(__name__)


def post_chat_message_to_discord(_, log):
    if not DISCORD_CHAT_WEBHOOK_URL:
        return
    if not WEBHOOK_ID:
        return
    if not WEBHOOK_TOKEN:
        return

    try:
        message = log["message"]
        message = discord.utils.escape_mentions(message)
        message = discord.utils.escape_markdown(message)

        webhook = Webhook.partial(
            id=WEBHOOK_ID, token=WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter()
        )
        logger.info("sending chat message len=%s to Discord", len(message))
        webhook.send(message)

    except Exception as e:
        logger.error("error executing chat message webhook: %s", e)


def parse_webhook_url(url):
    """Parse and check validity of Discord webhook URL
    by performing a get request and checking existence
    of 'id' and 'token' in the JSON response.
    """
    try:
        resp = requests.get(url).json()
        _id = int(resp["id"])
        token = resp["token"]
        return _id, token
    except Exception as e:
        logger.error("error parsing Discord chat webhook url: %s", e)
        return None, None


# Only parse ID and token and apply decorator if webhook URL was provided.
if DISCORD_CHAT_WEBHOOK_URL:
    WEBHOOK_ID, WEBHOOK_TOKEN = parse_webhook_url(DISCORD_CHAT_WEBHOOK_URL)
    post_chat_message_to_discord = on_chat(post_chat_message_to_discord)
    logger.info("Discord chat webhook initialized")
