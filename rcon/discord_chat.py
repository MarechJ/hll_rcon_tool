import logging
import os

import discord.utils
import requests
from discord import RequestsWebhookAdapter
from discord import Webhook

from rcon.game_logs import on_chat
from rcon.game_logs import on_kill
from rcon.game_logs import on_tk

DISCORD_CHAT_WEBHOOK_URL = os.getenv("DISCORD_CHAT_WEBHOOK")
DISCORD_KILLS_WEBHOOK_URL = os.getenv("DISCORD_KILLS_WEBHOOK")
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


def escape_string(string):
    string = discord.utils.escape_markdown(string)
    string = discord.utils.escape_mentions(string)
    return string


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


class DiscordWebhookHandler:
    """ RCON Tool -> Discord messaging.
    TODO: refactor duplicates.
    TODO: singleton to avoid initializing env vars multiple times?
    """

    INITIALIZED = False
    PING_TRIGGER_WORDS = []
    PING_TRIGGER_ROLES = []
    CHAT_WEBHOOK = None
    KILLS_WEBHOOK = None
    SEND_KILLS = False
    SEND_TEAM_KILLS = False

    @classmethod
    def init_env_vars(cls):
        cls.init_ping_trigger_vars()
        cls.init_chat_vars()
        cls.init_kill_vars()

    @classmethod
    def init_ping_trigger_vars(cls):
        try:
            cls.PING_TRIGGER_WORDS = [
                word.lower().strip()
                for word in PING_TRIGGER_WORDS.split(",") if word
            ]
            cls.PING_TRIGGER_ROLES = [
                role.strip()
                for role in PING_TRIGGER_ROLES.split(",") if role
            ]
            logger.info("ping trigger variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing ping trigger variables: %s", e)

    @classmethod
    def init_chat_vars(cls):
        try:
            cls.CHAT_WEBHOOK = parse_webhook_url(DISCORD_CHAT_WEBHOOK_URL)
            logger.info("chat variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing chat variables: %s", e)

    @classmethod
    def init_kill_vars(cls):
        try:
            cls.KILLS_WEBHOOK = parse_webhook_url(DISCORD_KILLS_WEBHOOK_URL)
            cls.SEND_KILLS = True if SEND_KILLS == "yes" else False
            cls.SEND_TEAM_KILLS = True if SEND_TEAM_KILLS == "yes" else False
            logger.info("kill variables initialized successfully")
        except Exception as e:
            logger.exception("error initializing kill variables: %s", e)

    @classmethod
    def send_chat_message(cls, _, log):
        if not cls.CHAT_WEBHOOK:
            return

        try:
            webhook_id = cls.CHAT_WEBHOOK[0]
            webhook_token = cls.CHAT_WEBHOOK[1]
            message = log["sub_content"]

            if ALLOW_MENTIONS != 'yes':
                message = discord.utils.escape_mentions(message)
            message = discord.utils.escape_markdown(message)

            webhook = Webhook.partial(
                id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
            )
            player = log["player"].ljust(25)
            steam_id = log["steam_id_64_1"]
            action = log["action"]
            action = action.split("CHAT")[1]
            color = CHAT_ACTION_TO_COLOR[action]

            embed = discord.Embed(description=message,
                                  color=color)
            embed.set_author(name=f"{player} {action}",
                             url=STEAM_PROFILE_URL.format(id64=steam_id))

            content = None
            if cls.PING_TRIGGER_WORDS:
                msg_words = message.split()
                for trigger_word in cls.PING_TRIGGER_WORDS:
                    for i, msg_word in enumerate(msg_words):
                        if trigger_word == msg_word.lower():
                            content = " ".join(cls.PING_TRIGGER_ROLES)
                            msg_words[i] = f"__**{msg_words[i]}**__"
                            embed.description = " ".join(msg_words)
                            break  # TODO: handle all trigger words?

            logger.debug("sending chat message len=%s to Discord",
                         len(embed) + len(content) if content else 0)
            webhook.send(content=content, embed=embed)

        except Exception as e:
            logger.exception("error executing chat message webhook: %s", e)

    @classmethod
    def send_kill_message(cls, _, log):
        if not cls.KILLS_WEBHOOK:
            return

        try:
            action = log["action"]
            if action == "KILL" and not cls.SEND_KILLS:
                return
            elif action == "TEAM KILL" and not cls.SEND_TEAM_KILLS:
                return

            webhook_id = cls.KILLS_WEBHOOK[0]
            webhook_token = cls.KILLS_WEBHOOK[1]
            webhook = Webhook.partial(
                id=webhook_id, token=webhook_token, adapter=RequestsWebhookAdapter()
            )

            player1 = escape_string(log["player"])
            player2 = escape_string(log["player2"])
            id_1 = log["steam_id_64_1"]
            killer_id_link = f"[{player1}]({STEAM_PROFILE_URL.format(id64=id_1)})"
            id_2 = log["steam_id_64_2"]
            victim_id_link = f"[{player2}]({STEAM_PROFILE_URL.format(id64=id_2)})"

            color = KILL_ACTION_TO_COLOR[action]
            killer_field_name = {
                "KILL": "Killer",
                "TEAM KILL": "Team Killer",
            }[action]

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
                name="\u200b",
                value="\u200b",
            ).add_field(
                name="Weapon",
                value=log["weapon"],
            )

            logger.debug("sending kill message len=%s to Discord", len(embed))
            webhook.send(embed=embed)
        except Exception as e:
            logger.exception("error executing kill message webhook %s", e)


# TODO: Check how to properly decorate class methods with hooks
#  and move the decorators inside the class.
DiscordWebhookHandler.send_chat_message = on_chat(DiscordWebhookHandler.send_chat_message)
DiscordWebhookHandler.send_kill_message = on_kill(on_tk(DiscordWebhookHandler.send_kill_message))
