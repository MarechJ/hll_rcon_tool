import logging
from datetime import datetime
from discord_webhook import DiscordWebhook
import os
from rconweb.settings import ENVIRONMENT

logger = logging.getLogger('rconweb')

def send_to_discord_audit(message, by=None, silent=True):
    webhookurl = os.getenv('DISCORD_WEBHOOK_AUDIT_LOG', None)
    if not webhookurl:
        return
    try:
        webhook = DiscordWebhook(url=webhookurl, content='[{}][{}][{}] {}'.format(datetime.now().isoformat(), ENVIRONMENT, by, message))
        return webhook.execute()
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise