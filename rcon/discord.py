from discord_webhook import DiscordWebhook
import os

def send_to_discord_audit(message):
    webhookurl = os.getenv('DISCORD_WEBHOOK_AUDIT_LOG', None)
    if not webhookurl:
        return
    webhook = DiscordWebhook(url=webhookurl, content='test')
    return webhook.execute()