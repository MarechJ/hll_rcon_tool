import logging
import os
from functools import lru_cache

import discord.utils
import requests
from discord import RequestsWebhookAdapter
from discord import Webhook

from rcon.game_logs import on_chat
from rcon.game_logs import on_kill
from rcon.game_logs import on_tk

DISCORD_CHAT_WEBHOOK_URL = os.getenv("DISCORD_CHAT_WEBHOOK")
DISCORD_KILLS_WEBHOOK_URL = os.getenv("DISCORD_KILLS_WEBHOOK")
PING_TRIGGER_WEBHOOK = os.getenv("DISCORD_PING_TRIGGER_WEBHOOK")
ALLOW_MENTIONS = os.getenv("DISCORD_CHAT_WEBHOOK_ALLOW_MENTIONS")
PING_TRIGGER_WORDS = os.getenv("DISCORD_PING_TRIGGER_WORDS")
PING_TRIGGER_ROLES = os.getenv("DISCORD_PING_TRIGGER_ROLES")
SEND_KILLS = os.getenv("DISCORD_SEND_KILL_UPDATES")
SEND_TEAM_KILLS = os.getenv("DISCORD_SEND_TEAM_KILL_UPDATES")

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


@lru_cache
def parse_webhook_url(url):
    """Parse and check validity of Discord webhook URL
    by performing a get request and checking existence
    of 'id' and 'token' in the JSON response.
    """
    if not url:
        logger.info("no Discord chat webhook URL provided")
        return None
    resp = requests.get(url).json()
    _id = int(resp["id"])
    token = resp["token"]
    return _id, token


def make_hook(webhook_url):
    webhook_id, webhook_token = parse_webhook_url(webhook_url)
    return Webhook.partial(
        id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
    )


class DiscordWebhookHandler:
    """RCON Tool -> Discord messaging."""

    def __init__(self):
        # TODO: take config as argument if modularity is desired.
        self.ping_trigger_words = []
        self.ping_trigger_roles = []
        self.chat_webhook = None
        self.kills_webhook = None
        self.ping_trigger_webhook = None
        self.send_kills = False
        self.send_team_kills = False
        self.init_env_vars()

    def init_env_vars(self):
        self.init_ping_trigger_vars()
        self.init_chat_vars()
        self.init_kill_vars()

    def init_ping_trigger_vars(self):
        try:
            self.ping_trigger_words = [
                word.lower().strip()
                for word in PING_TRIGGER_WORDS.split(",") if word
            ]
            self.ping_trigger_roles = [
                role.strip()
                for role in PING_TRIGGER_ROLES.split(",") if role
            ]
            self.ping_trigger_webhook = make_hook(PING_TRIGGER_WEBHOOK)
            logger.info("ping trigger variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing ping trigger variables: %s", e)

    def init_chat_vars(self):
        try:
            self.chat_webhook = make_hook(DISCORD_CHAT_WEBHOOK_URL)
            logger.info("chat variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing chat variables: %s", e)

    def init_kill_vars(self):
        try:
            self.kills_webhook = make_hook(DISCORD_KILLS_WEBHOOK_URL)
            self.send_kills = True if SEND_KILLS == "yes" else False
            self.send_team_kills = True if SEND_TEAM_KILLS == "yes" else False
            logger.info("kill variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing kill variables: %s", e)

    def send_chat_message(self, _, log):
        if not self.chat_webhook:
            return

        try:
            message = log["sub_content"]

            if ALLOW_MENTIONS != 'yes':
                message = discord.utils.escape_mentions(message)
            message = discord.utils.escape_markdown(message)

            player = log["player"].ljust(25)
            steam_id = log["steam_id_64_1"]
            action = log["action"]
            action = action.split("CHAT")[1]
            color = CHAT_ACTION_TO_COLOR[action]

            embed = discord.Embed(description=message,
                                  color=color)
            embed.set_author(name=f"{player} {action}",
                             url=STEAM_PROFILE_URL.format(id64=steam_id))

            content = ""
            triggered = False
            if self.ping_trigger_words:
                msg_words = message.split()
                for trigger_word in self.ping_trigger_words:
                    for i, msg_word in enumerate(msg_words):
                        if trigger_word == msg_word.lower():
                            triggered = True
                            content = " ".join(self.ping_trigger_roles)
                            msg_words[i] = f"__**{msg_words[i]}**__"
                if triggered:
                    embed.description = " ".join(msg_words)

            logger.debug("sending chat message len=%s to Discord",
                         len(embed) + len(content))

            # Use chat webhook for both.
            if ((self.ping_trigger_webhook == self.chat_webhook)
                    or not self.ping_trigger_webhook):
                self.chat_webhook.send(content=content, embed=embed)
            # Use separate webhooks.
            else:
                self.chat_webhook.send(embed=embed)
                if triggered:
                    self.ping_trigger_webhook.send(content=content, embed=embed)

        except Exception as e:
            logger.exception("error executing chat message webhook: %s", e)

    def send_generic_kill_message(self, _, log, action):
        if not self.kills_webhook:
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
            self.kills_webhook.send(embed=embed)
        except Exception as e:
            logger.exception("error executing kill message webhook %s", e)

    def send_kill_message(self, _, log):
        action = log["action"]
        if action == "KILL" and not self.send_kills:
            self.send_generic_kill_message(_, log, action)

    def send_tk_message(self, _, log):
        action = log["action"]
        if action == "TEAM KILL" and not self.send_team_kills:
            self.send_generic_kill_message(_, log, action)


HANDLER = DiscordWebhookHandler()


@on_chat
def handle_on_chat(rcon, log):
    HANDLER.send_chat_message(rcon, log)


@on_kill
def handle_on_kill(rcon, log):
    HANDLER.send_kill_message(rcon, log)


@on_tk
def handle_on_tk(rcon, log):
    HANDLER.send_tk_message(rcon, log)
