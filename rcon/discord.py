import logging
from datetime import datetime
from discord_webhook import DiscordWebhook
import os

logger = logging.getLogger(__name__)

def dict_to_discord(d):
    return "   ".join([f"{k}: `{v}`" for k, v in d.items()])


def send_to_discord_audit(message, by=None, silent=True):
    webhookurl = os.getenv('DISCORD_WEBHOOK_AUDIT_LOG', None)
    logger.info("Audit: [%s] %s", by, message)
    if not webhookurl:
        logger.debug("No webhook set for audit log")
        return
    try:
        server_name = os.getenv('SERVER_SHORT_NAME', os.getenv('SERVER_SHORT_NAME', 'Undefined'))
        webhook = DiscordWebhook(url=webhookurl, content='[{}][**{}**] {}'.format(server_name, by, message))
        return webhook.execute()
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise