import datetime
import logging
import os
import pathlib
import sqlite3
import time
from sqlite3 import Connection
from typing import TypedDict
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError, RequestException

import discord
from discord.embeds import Embed
from discord.errors import HTTPException, NotFound
from rcon.cache_utils import ttl_cache
from rcon.config import get_config
from rcon.user_config.scorebot import ScorebotUserConfig, StatTypes


class _PublicInfoCurrentMapType(TypedDict):
    just_name: str
    human_name: str
    name: str
    start: int


class _PublicInfoNextMapType(TypedDict):
    just_name: str
    human_name: str
    name: str
    start: int | None


class _PublicInfoPlayerType(TypedDict):
    allied: int
    axis: int


class _PublicInfoScoreType(TypedDict):
    allied: str
    axis: str


class _PublicInfoVoteStatusType(TypedDict):
    total_votes: int
    winning_maps: list[str]


class _PublicInfoNameType(TypedDict):
    name: str
    short_name: str
    public_stats_port: str
    public_stats_port_https: str


class PublicInfoType(TypedDict):
    """TypedDict for rcon.views.public_info"""

    current_map: _PublicInfoCurrentMapType
    next_map: _PublicInfoNextMapType
    player_count: int
    max_player_count: int
    players: _PublicInfoPlayerType
    score: _PublicInfoScoreType
    raw_time_remaining: str
    vote_status: _PublicInfoVoteStatusType
    name: _PublicInfoNameType


logger = logging.getLogger("rcon")

# try:
#     config = get_config()

#     SERVER_CONFIG = config["SCOREBOT"][f'SERVER_{os.getenv("SERVER_NUMBER")}']
#     CONFIG = config["SCOREBOT"]["COMMON"]

#     STATS_URL = SERVER_CONFIG["STATS_URL"]
#     INFO_URL = SERVER_CONFIG["INFO_URL"]
#     SCOREBOARD_PUBLIC_URL = SERVER_CONFIG["SCOREBOARD_PUBLIC_URL"]

#     try:
#         # Older versions of default_config.yml and peoples config.yml have this typo
#         SCOREBOARD_BASE_PATH = SERVER_CONFIG["SCORBOARD_BASE_PATH"]
#     except KeyError:
#         SCOREBOARD_BASE_PATH = SERVER_CONFIG["SCOREBOARD_BASE_PATH"]

#     PAST_GAMES_URL = SERVER_CONFIG["PAST_GAMES_URL"]
#     WEBHOOK_URL = SERVER_CONFIG["WEBHOOK_URL"]

#     ALL_STATS_TEXT = CONFIG["ALL_STATS_TEXT"]
#     AUTHOR_NAME = CONFIG["AUTHOR_NAME"]
#     AUTHOR_ICON_URL = CONFIG["AUTHOR_ICON_URL"]
#     TOP_LIMIT = CONFIG["TOP_LIMIT"]
#     FOOTER_ICON_URL = CONFIG["FOOTER_ICON_URL"]
#     NO_STATS_AVAILABLE = CONFIG["NO_STATS_AVAILABLE"]
#     FIND_PAST_STATS = CONFIG["FIND_PAST_STATS"]
#     NEXT_MAP_TEXT = CONFIG["NEXT_MAP_TEXT"]
#     VOTE = CONFIG["VOTE"]
#     PLAYERS = CONFIG["PLAYERS"]
#     ELAPSED_TIME = CONFIG["ELAPSED_TIME"]

#     # New options, including defaults to not break it for users with an older config.yml
#     ALLIED_PLAYERS_TEXT = CONFIG.get("ALLIED_PLAYERS_TEXT", "Allied Players")
#     AXIS_PLAYERS_TEXT = CONFIG.get("AXIS_PLAYERS_TEXT", "Axis Players")
#     MATCH_SCORE_TITLE_TEXT = CONFIG.get("MATCH_SCORE_TITLE_TEXT", "Match Score")
#     MATCH_SCORE_TEXT = CONFIG.get("MATCH_SCORE_TEXT", "Allied {0} : Axis {1}")
#     TIME_REMAINING_TEXT = CONFIG.get("TIME_REMAINING_TEXT", "Time Remaining")

#     TOP_KILLERS = CONFIG["TOP_KILLERS"]
#     TOP_RATIO = CONFIG["TOP_RATIO"]
#     TOP_PERFORMANCE = CONFIG["TOP_PERFORMANCE"]
#     TRY_HARDERS = CONFIG["TRY_HARDERS"]
#     TOP_STAMINA = CONFIG["TOP_STAMINA"]
#     TOP_KILL_STREAK = CONFIG["TOP_KILL_STREAK"]
#     MOST_PATIENT = CONFIG["MOST_PATIENT"]
#     I_NEVER_GIVE_UP = CONFIG["I_NEVER_GIVE_UP"]
#     I_M_CLUMSY = CONFIG["I_M_CLUMSY"]
#     I_NEED_GLASSES = CONFIG["I_NEED_GLASSES"]
#     I_LOVE_VOTING = CONFIG["I_LOVE_VOTING"]
#     WHAT_IS_A_BREAK = CONFIG["WHAT_IS_A_BREAK"]
#     SURVIVORS = CONFIG["SURVIVORS"]
#     U_R_STILL_A_MAN = CONFIG["U_R_STILL_A_MAN"]

#     STATS_KEYS_TO_DISPLAY = CONFIG["STATS_TO_DISPLAY"]
# except Exception as e:
#     logger.exception(f"There's an error in your scorebot config: {repr(e)}")
#     raise


map_to_pict = {
    "carentan": "maps/carentan.webp",
    "driel": "maps/driel.webp",
    "elalamein": "maps/elalamein.webp",
    "foy": "maps/foy.webp",
    "hill400": "maps/hill400.webp",
    "hurtgenforest": "maps/hurtgen.webp",
    "kharkov": "maps/kharkov.webp",
    "kursk": "maps/kursk.webp",
    "omahabeach": "maps/omaha.webp",
    "purpleheartlane": "maps/phl.webp",
    "stalingrad": "maps/stalingrad.webp",
    "stmariedumont": "maps/smdm.webp",
    "stmereeglise": "maps/sme.webp",
    "utahbeach": "maps/utah.webp",
}


def get_map_image(server_info, config: ScorebotUserConfig):
    img = map_to_pict.get(
        server_info["current_map"]["just_name"], server_info["current_map"]["just_name"]
    )
    url = urljoin(config.base_scoreboard_url, img)
    return url


def get_header_embed(public_info: PublicInfoType, config: ScorebotUserConfig):
    elapsed_time_minutes = (
        datetime.datetime.now()
        - datetime.datetime.fromtimestamp(public_info["current_map"]["start"])
    ).total_seconds() / 60

    embed = discord.Embed(
        title=f"{public_info['name']}",
        description=f"**{public_info['current_map']['human_name']} - {config.elapsed_time_text}{round(elapsed_time_minutes)} min. - {public_info['player_count']}/{public_info['max_player_count']} {config.players_text}**",
        color=13734400,
        timestamp=datetime.datetime.utcnow(),
        url=config.base_scoreboard_url,
    )
    total_votes = public_info["vote_status"]["total_votes"]
    winning_map_votes = 0
    if len(public_info["vote_status"]["winning_maps"]) >= 1:
        winning_map_votes = public_info["vote_status"]["winning_maps"][0][1]

    embed.add_field(
        name=f"{config.next_map_text} {public_info['next_map']['human_name']}",
        value=f"{winning_map_votes}/{total_votes} {config.vote_text}",
    )

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name=f"{config.allied_players_text}",
        value=f"{public_info['players']['allied']}",
        inline=True,
    )

    embed.add_field(
        name=f"{config.axis_players_text}",
        value=f"{public_info['players']['axis']}",
        inline=True,
    )

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name=f"{config.match_score_title_text}",
        value=config.match_score_text.format(
            public_info["score"]["allied"], public_info["score"]["axis"]
        ),
        inline=True,
    )

    embed.add_field(
        name=f"{config.time_remaining_text}",
        value=f"{public_info['raw_time_remaining']}",
        inline=True,
    )

    embed.set_author(
        name=config.author_name_text,
        url=config.base_scoreboard_url,
        icon_url=config.author_icon_url,
    )
    embed.set_image(url=get_map_image(public_info, config))

    return embed


def escaped_name(stat):
    return (
        stat["player"]
        .replace("#", " ")
        .replace("[", "")
        .replace("]", "")
        .replace("```", "")
    )


def get_stat(stats, key, limit: int, post_process=lambda v: v, reverse=True, **kwargs):
    stats = sorted(stats, key=lambda stat: stat[key], reverse=reverse)[:limit]

    return "```md\n%s\n```" % "\n".join(
        f"[#{rank}][{escaped_name(stat)}]: {post_process(stat[key])}"
        for rank, stat in enumerate(stats, start=1)
    )


def get_embeds(server_info, stats, config: ScorebotUserConfig):
    embeds = []
    embeds.append(get_header_embed(server_info, config))

    stat_display_lookup = {
        "top_killers": "kills",
        "top_ratio": "kill_death_ratio",
        "top_performance": "kills_per_minute",
        "try_harders": "deaths_per_minute",
        "top_stamina": "deaths",
        "top_kill_streak": "kills_streak",
        "i_never_give_up": "deaths_without_kill_streak",
        "most_patient": "deaths_by_tk",
        "im_clumsy": "teamkills",
        "i_need_glasses": "teamkills_streak",
        "i_love_voting": "nb_vote_started",
        "what_is_a_break": "time_seconds",
        "survivors": "longest_life_secs",
        "u_r_still_a_man": "shortest_life_secs",
    }

    current_embed = Embed(
        color=13734400,
    )
    if not stats:
        current_embed.add_field(
            name=config.no_stats_available_text,
            value=f"{config.find_past_stats_text}{config.past_games_url}",
        )
        embeds.append(current_embed)
    else:
        for idx, stat_display in enumerate(config.stats_to_display):
            logger.warning(f"{stat_display=}")
            current_embed.add_field(
                name=stat_display.display_format,
                value=get_stat(
                    stats, stat_display_lookup[stat_display.type], config.top_limit
                ),
            )
            if idx % 2:
                embeds.append(current_embed)
                current_embed = Embed(
                    color=13734400,
                )

    embeds[-1].add_field(
        name="\u200b",
        value=f"{config.all_stats_text}{config.base_scoreboard_url}",
        inline=False,
    )
    embeds[-1].set_footer(
        icon_url=config.footer_icon_url, text="Community RCon based stats by Dr.WeeD"
    )
    print(embeds)
    return embeds


def get_stats(stats_url: str):
    stats = requests.get(stats_url, verify=False).json()
    try:
        stats = stats["result"]["stats"]
    except KeyError:
        stats = stats["result"]["player_stats"]

    return stats


def cleanup_orphaned_messages(conn: Connection, server_number: int, webhook_url: str):
    conn.execute(
        "DELETE FROM stats_messages WHERE server_number = ? AND message_type = ? AND webhook = ?",
        (server_number, "live", webhook_url),
    )
    conn.commit()


@ttl_cache(ttl=5 * 60 * 60)
def refresh_config() -> ScorebotUserConfig:
    config = ScorebotUserConfig.load_from_db()
    return config


def create_table(conn):
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stats_messages (
                server_number INT,
                message_type VARCHAR(50),
                message_id VARCHAR(200),
                webhook VARCHAR(500)
            )
            """
        )
        conn.commit()
    except Exception as e:
        logger.exception(e)


def fetch_existing(conn, server_number: int, webhook_url: str):
    message_id = conn.execute(
        "SELECT message_id FROM stats_messages WHERE server_number = ? AND message_type = ? AND webhook = ?",
        (server_number, "live", webhook_url),
    )
    message_id = message_id.fetchone()

    return message_id


def run():
    config = refresh_config()
    try:
        path = os.getenv("DISCORD_BOT_DATA_PATH", "/data")
        path = pathlib.Path(path) / pathlib.Path("scorebot.db")
        conn = sqlite3.connect(str(path))
        server_number = int(os.getenv("SERVER_NUMBER", 0))
        # TODO handle webhook change
        # TODO handle invalid message id

        webhooks = [
            discord.Webhook.from_url(
                webhook_url,
                adapter=discord.RequestsWebhookAdapter(),
            )
            for webhook_url in config.webhook_urls
        ]

        try:
            public_info = requests.get(config.info_url, verify=False).json()["result"]
        except ConnectionError as e:
            logger.error(f"Error accessing {config.info_url}")
            raise

        stats = get_stats(config.stats_url)
        for webhook in webhooks:
            message_id = fetch_existing(conn, server_number, webhook.url)

            if message_id:
                (message_id,) = message_id
                logger.info("Resuming with message_id %s" % message_id)
            else:
                message = webhook.send(
                    embeds=get_embeds(public_info, stats, config), wait=True
                )
                conn.execute(
                    "INSERT INTO stats_messages VALUES (?, ?, ?, ?)",
                    (server_number, "live", message.id, webhook.url),
                )
                conn.commit()
                message_id = message.id

        while True:
            config = refresh_config()
            public_info = requests.get(config.info_url, verify=False).json()["result"]
            stats = get_stats(config.stats_url)

            for webhook in webhooks:
                try:
                    webhook.edit_message(
                        message_id, embeds=get_embeds(public_info, stats, config)
                    )
                except NotFound as ex:
                    logger.exception(
                        "Message with ID in our records does not exist, cleaning up and restarting"
                    )
                    cleanup_orphaned_messages(conn, server_number, webhook.url)
                    raise ex
                except (HTTPException, RequestException, ConnectionError):
                    logger.exception("Temporary failure when trying to edit message")
                    time.sleep(5)
                except Exception as e:
                    logger.exception("Unable to edit message. Deleting record", e)
                    cleanup_orphaned_messages(conn, server_number, webhook.url)
                    raise e
                time.sleep(1)
    except Exception as e:
        logger.exception("The bot stopped", e)
        raise


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(e)
        raise
