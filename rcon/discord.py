import logging
from datetime import datetime
from discord_webhook import DiscordWebhook
import os

logger = logging.getLogger('rconweb')

def dict_to_discord(d):
    return "   ".join([f"{k}: `{v}`" for k, v in d.items()])


def send_to_discord_audit(message, by=None, silent=True):
    webhookurl = os.getenv('DISCORD_WEBHOOK_AUDIT_LOG', None)
    if not webhookurl:
        return
    try:
        server_name = os.getenv('SERVER_SHORT_NAME', os.getenv('SERVER_SHORT_NAME', 'Undefined'))
        webhook = DiscordWebhook(url=webhookurl, content='[{}][**{}**] {}'.format(server_name, by, message))
        return webhook.execute()
    except:
        logger.exception("Can't send audit log")
        if not silent:
            raise