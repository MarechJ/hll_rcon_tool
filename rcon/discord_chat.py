import logging
import os
import re
from datetime import datetime
from functools import lru_cache

import discord.utils

from rcon.game_logs import on_chat, on_kill, on_tk
from rcon.rcon_discord import make_hook
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    ChatWebhooksUserConfig,
    KillsWebhooksUserConfig,
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

    def __init__(self):
        self.admin_wh_config = AdminPingWebhooksUserConfig.load_from_db()
        self.chat_wh_config = ChatWebhooksUserConfig.load_from_db()
        self.kills_wh_config = KillsWebhooksUserConfig.load_from_db()
        self.server_settings = RconServerSettingsUserConfig.load_from_db()

        ping_trigger_webhooks = []
        try:
            ping_trigger_webhooks = [
                make_hook(hook.url) for hook in self.admin_wh_config.hooks
            ]
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        chat_webhooks = []
        try:
            chat_webhooks = [make_hook(hook.url) for hook in self.chat_wh_config.hooks]
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        kills_webhooks = []
        try:
            kills_webhooks = [
                make_hook(hook.url) for hook in self.kills_wh_config.hooks
            ]
        except Exception as e:
            logger.exception("Error initializing ping trigger webhooks: %s", e)

        self.ping_trigger_webhooks = [wh for wh in ping_trigger_webhooks if wh]
        self.chat_webhooks = [wh for wh in chat_webhooks if wh]
        self.kills_webhooks = [wh for wh in kills_webhooks if wh]

    def send_chat_message(self, _, log):
        try:
            message = log["sub_content"]

            if not self.chat_wh_config.allow_mentions:
                message = discord.utils.escape_mentions(message)
            message = discord.utils.escape_markdown(message)

            player = log["player"].ljust(25)
            steam_id = log["steam_id_64_1"]
            action = log["action"]
            action = action.split("CHAT")[1]
            color = CHAT_ACTION_TO_COLOR[action]

            embed = discord.Embed(
                description=message, color=color, timestamp=datetime.utcnow()
            )
            embed.set_author(
                name=f"{player} {action}", url=STEAM_PROFILE_URL.format(id64=steam_id)
            )
            embed.set_footer(text=self.server_settings.short_name)

            content = ""
            triggered = False
            if self.admin_wh_config.trigger_words:
                msg_words = re.split("([^a-zA-Z!@])", message)
                for trigger_word in self.admin_wh_config.trigger_words:
                    for i, msg_word in enumerate(msg_words):
                        if trigger_word == msg_word.lower():
                            triggered = True
                            msg_words[i] = f"__**{msg_words[i]}**__"
                if triggered:
                    mentions: list[str] = []
                    mentions.extend(
                        [
                            id_
                            for h in self.admin_wh_config.hooks
                            for id_ in h.user_mentions
                        ]
                    )
                    mentions.extend(
                        [
                            id_
                            for h in self.admin_wh_config.hooks
                            for id_ in h.role_mentions
                        ]
                    )
                    content = " ".join(mentions)
                    embed.description = "".join(msg_words)

            logger.debug(
                "sending chat message len=%s to Discord", len(embed) + len(content)
            )

            if self.chat_webhooks:
                for wh in self.chat_webhooks:
                    wh.send(content=content, embed=embed)

            if triggered and self.ping_trigger_webhooks:
                for wh in self.ping_trigger_webhooks:
                    wh.send(content=content, embed=embed)
        except Exception as e:
            logger.exception("error executing chat message webhook: %s", e)
            raise

    def send_generic_kill_message(self, _, log, action):
        if not self.kills_webhooks:
            return

        try:
            player1 = escape_string(log["player"])
            player2 = escape_string(log["player2"])
            id_1 = log["steam_id_64_1"]
            killer_id_link = f"[{player1}]({STEAM_PROFILE_URL.format(id64=id_1)})"
            id_2 = log["steam_id_64_2"]
            victim_id_link = f"[{player2}]({STEAM_PROFILE_URL.format(id64=id_2)})"

            color = KILL_ACTION_TO_COLOR[action]

            # "TEAM KILL" -> "Team Killer", etc.
            killer_field_name = f"{action.title().strip()}er"

            embed = discord.Embed(color=color)
            embed.add_field(
                name=killer_field_name,
                value=killer_id_link,
                inline=True,
            ).add_field(
                name="Victim",
                value=victim_id_link,
                inline=True,
            ).add_field(
                name="Weapon",
                value=log["weapon"],
                inline=True,
            )

            logger.debug("sending kill message len=%s to Discord", len(embed))
            for wh in self.kills_webhooks:
                wh.send(embed=embed)
        except Exception as e:
            logger.exception("error executing kill message webhook %s", e)

    def send_kill_message(self, _, log):
        action = log["action"]
        if action == "KILL" and self.kills_wh_config.send_kills:
            self.send_generic_kill_message(_, log, action)

    def send_tk_message(self, _, log):
        action = log["action"]
        if action == "TEAM KILL" and self.kills_wh_config.send_team_kills:
            self.send_generic_kill_message(_, log, action)


HANDLER = None


def get_handler():
    global HANDLER
    if not HANDLER:
        HANDLER = DiscordWebhookHandler()
    return HANDLER


@on_chat
def handle_on_chat(rcon, log):
    get_handler().send_chat_message(rcon, log)


@on_kill
def handle_on_kill(rcon, log):
    get_handler().send_kill_message(rcon, log)


@on_tk
def handle_on_tk(rcon, log):
    get_handler().send_tk_message(rcon, log)
