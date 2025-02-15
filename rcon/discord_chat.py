import logging
import re
from datetime import datetime
from functools import lru_cache
from typing import Iterable

from discord_webhook import DiscordEmbed, DiscordWebhook

import discord.utils
from rcon.utils import get_server_number
from rcon.cache_utils import ttl_cache
from rcon.discord import make_hook
from rcon.logs.loop import on_chat, on_kill, on_tk
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    ChatWebhooksUserConfig,
    DiscordMentionWebhook,
    DiscordWebhook,
    KillsWebhooksUserConfig,
)
from rcon.webhook_service import (
    enqueue_message,
    WebhookMessage,
    WebhookType,
    WebhookMessageType,
)

STEAM_PROFILE_URL = "http://steamcommunity.com/profiles/{id64}"

RED = 0xA62019
LIGHT_RED = 0xF93A2F
BLUE = 0x006798
LIGHT_BLUE = 0x0099E1
GREEN = 0x07DA63

KILL_ACTION_TO_COLOR = {
    "KILL": GREEN,
    "TEAM KILL": LIGHT_RED,
}
CHAT_ACTION_TO_COLOR = {
    "[Axis][Team]": LIGHT_RED,
    "[Axis][Unit]": RED,
    "[Allies][Team]": LIGHT_BLUE,
    "[Allies][Unit]": BLUE,
}

logger = logging.getLogger(__name__)


@lru_cache
def escape_string(string):
    string = discord.utils.escape_markdown(string)
    string = discord.utils.escape_mentions(string)
    return string


class DiscordWebhookHandler:
    """RCON Tool -> Discord messaging."""

    def __init__(
        self,
        admin_wh_config: AdminPingWebhooksUserConfig | None = None,
        chat_wh_config: ChatWebhooksUserConfig | None = None,
        kills_wh_config: KillsWebhooksUserConfig | None = None,
        server_settings: RconServerSettingsUserConfig | None = None,
    ):
        self.admin_wh_config: AdminPingWebhooksUserConfig = (
            admin_wh_config or AdminPingWebhooksUserConfig.load_from_db()
        )
        self.chat_wh_config: ChatWebhooksUserConfig = (
            chat_wh_config or ChatWebhooksUserConfig.load_from_db()
        )
        self.kills_wh_config: KillsWebhooksUserConfig = (
            kills_wh_config or KillsWebhooksUserConfig.load_from_db()
        )
        self.server_settings: RconServerSettingsUserConfig = (
            server_settings or RconServerSettingsUserConfig.load_from_db()
        )

        ping_trigger_webhooks = []
        try:
            ping_trigger_webhooks = self._make_hook(self.admin_wh_config.hooks)
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        chat_webhooks = []
        try:
            chat_webhooks = self._make_hook(self.chat_wh_config.hooks)
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        kills_webhooks = []
        try:
            kills_webhooks = self._make_hook(self.kills_wh_config.hooks)
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        # TODO: If we don't get a valid response for a webhook we should log it
        self.ping_trigger_webhooks = [wh for wh in ping_trigger_webhooks if wh]
        self.chat_webhooks = [wh for wh in chat_webhooks if wh]
        self.kills_webhooks = [wh for wh in kills_webhooks if wh]

    @staticmethod
    def _make_hook(hooks: Iterable[DiscordWebhook] | Iterable[DiscordMentionWebhook]):
        return [make_hook(hook.url) for hook in hooks]

    def create_chat_embed(self, log, allow_mentions=False) -> DiscordEmbed:
        message = log["sub_content"]

        if not allow_mentions:
            message = discord.utils.escape_mentions(message)
        message = discord.utils.escape_markdown(message)

        player = log["player_name_1"].ljust(25)
        player_id = log["player_id_1"]
        action = log["action"]
        action = action.split("CHAT")[1]
        color = CHAT_ACTION_TO_COLOR[action]

        embed = DiscordEmbed(
            description=message, color=color, timestamp=datetime.utcnow()
        )
        embed.set_author(
            name=f"{player} {action}", url=STEAM_PROFILE_URL.format(id64=player_id)
        )
        embed.set_footer(text=self.server_settings.short_name)

        return embed

    def create_admin_ping_message(self, log) -> tuple[str, DiscordEmbed, bool]:
        message = log["sub_content"]
        embed = self.create_chat_embed(log)

        content = ""
        triggered = False
        if self.admin_wh_config.trigger_words:
            msg_words = re.split(r"([^a-zA-Z!@\d])", message)
            for trigger_word in self.admin_wh_config.trigger_words:
                for i, msg_word in enumerate(msg_words):
                    if trigger_word == msg_word.lower():
                        triggered = True
                        msg_words[i] = f"__**{msg_words[i]}**__"
            if triggered:
                mentions: list[str] = []
                mentions.extend(
                    [id_ for h in self.admin_wh_config.hooks for id_ in h.user_mentions]
                )
                mentions.extend(
                    [id_ for h in self.admin_wh_config.hooks for id_ in h.role_mentions]
                )
                content = " ".join(mentions)
                embed.description = discord.utils.escape_mentions("".join(msg_words))

        return content, embed, triggered

    def create_chat_message(self, log) -> DiscordEmbed:
        message = log["sub_content"]
        embed = self.create_chat_embed(
            log, allow_mentions=self.chat_wh_config.allow_mentions
        )

        return embed

    def create_kill_message(self, log):
        action = log["action"]
        player1 = escape_string(log["player_name_1"])
        player2 = escape_string(log["player_name_2"])
        id_1 = log["player_id_1"]
        killer_id_link = f"[{player1}]({STEAM_PROFILE_URL.format(id64=id_1)})"
        id_2 = log["player_id_2"]
        victim_id_link = f"[{player2}]({STEAM_PROFILE_URL.format(id64=id_2)})"

        color = KILL_ACTION_TO_COLOR[action]

        # "TEAM KILL" -> "Team Killer", etc.
        killer_field_name = f"{action.title().strip()}er"

        embed = DiscordEmbed(color=color)
        embed.add_embed_field(
            name=killer_field_name,
            value=killer_id_link,
            inline=True,
        )
        embed.add_embed_field(
            name="Victim",
            value=victim_id_link,
            inline=True,
        )
        embed.add_embed_field(
            name="Weapon",
            value=log["weapon"],
            inline=True,
        )

        return embed

    def send_chat_message(self, log):
        try:
            content, admin_embed, triggered = self.create_admin_ping_message(log)
            chat_embed = self.create_chat_message(log)

            for wh in self.chat_webhooks:
                wh.remove_embeds()
                wh.add_embed(chat_embed)
                enqueue_message(
                    message=WebhookMessage(
                        payload=wh.json,
                        webhook_type=WebhookType.DISCORD,
                        message_type=WebhookMessageType.LOG_LINE_CHAT,
                        server_number=int(get_server_number()),
                    )
                )

            if triggered:
                for wh in self.ping_trigger_webhooks:
                    wh.remove_embeds()
                    wh.add_embed(admin_embed)
                    wh.content = content
                    enqueue_message(
                        message=WebhookMessage(
                            payload=wh.json,
                            webhook_type=WebhookType.DISCORD,
                            message_type=WebhookMessageType.ADMIN_PING,
                            server_number=int(get_server_number()),
                        )
                    )
        except Exception as e:
            logger.exception("error enqueing chat message webhook: %s", e)
            raise

    def send_generic_kill_message(self, log):
        if not self.kills_webhooks:
            return

        try:
            if log["action"] == "KILL":
                type_ = message_type = WebhookMessageType.LOG_LINE_KILL
            else:
                message_type = WebhookMessageType.LOG_LINE_TEAMKILL
            embed = self.create_kill_message(log)
            # TODO: fix this, needs to be fixed upstream
            # logger.debug("sending kill message len=%s to Discord", len(embed))
            for wh in self.kills_webhooks:
                wh.remove_embeds()
                wh.add_embed(embed)
                enqueue_message(
                    message=WebhookMessage(
                        payload=wh.json,
                        webhook_type=WebhookType.DISCORD,
                        message_type=message_type,
                        server_number=int(get_server_number()),
                    )
                )
        except Exception as e:
            logger.exception("error enqueing kill message webhook %s", e)

    def send_kill_message(self, log):
        if log["action"] == "KILL" and self.kills_wh_config.send_kills:
            self.send_generic_kill_message(log)

    def send_tk_message(self, log):
        if log["action"] == "TEAM KILL" and self.kills_wh_config.send_team_kills:
            self.send_generic_kill_message(log)


HANDLER = None


@ttl_cache(5 * 60)
def get_handler():
    global HANDLER
    HANDLER = DiscordWebhookHandler()
    return HANDLER


@on_chat
def handle_on_chat(rcon, log):
    get_handler().send_chat_message(log)


@on_kill
def handle_on_kill(rcon, log):
    get_handler().send_kill_message(log)


@on_tk
def handle_on_tk(rcon, log):
    get_handler().send_tk_message(log)
