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
from rcon.config import get_config


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

try:
    config = get_config()

    SERVER_CONFIG = config["SCOREBOT"][f'SERVER_{os.getenv("SERVER_NUMBER")}']
    CONFIG = config["SCOREBOT"]["COMMON"]

    STATS_URL = SERVER_CONFIG["STATS_URL"]
    INFO_URL = SERVER_CONFIG["INFO_URL"]
    SCOREBOARD_PUBLIC_URL = SERVER_CONFIG["SCOREBOARD_PUBLIC_URL"]

    try:
        # Older versions of default_config.yml and peoples config.yml have this typo
        SCOREBOARD_BASE_PATH = SERVER_CONFIG["SCORBOARD_BASE_PATH"]
    except KeyError:
        SCOREBOARD_BASE_PATH = SERVER_CONFIG["SCOREBOARD_BASE_PATH"]

    PAST_GAMES_URL = SERVER_CONFIG["PAST_GAMES_URL"]
    WEBHOOK_URL = SERVER_CONFIG["WEBHOOK_URL"]

    ALL_STATS_TEXT = CONFIG["ALL_STATS_TEXT"]
    AUTHOR_NAME = CONFIG["AUTHOR_NAME"]
    AUTHOR_ICON_URL = CONFIG["AUTHOR_ICON_URL"]
    TOP_LIMIT = CONFIG["TOP_LIMIT"]
    FOOTER_ICON_URL = CONFIG["FOOTER_ICON_URL"]
    NO_STATS_AVAILABLE = CONFIG["NO_STATS_AVAILABLE"]
    FIND_PAST_STATS = CONFIG["FIND_PAST_STATS"]
    NEXT_MAP_TEXT = CONFIG["NEXT_MAP_TEXT"]
    VOTE = CONFIG["VOTE"]
    PLAYERS = CONFIG["PLAYERS"]
    ELAPSED_TIME = CONFIG["ELAPSED_TIME"]

    # New options, including defaults to not break it for users with an older config.yml
    ALLIED_PLAYERS_TEXT = CONFIG.get("ALLIED_PLAYERS_TEXT", "Allied Players")
    AXIS_PLAYERS_TEXT = CONFIG.get("AXIS_PLAYERS_TEXT", "Axis Players")
    MATCH_SCORE_TITLE_TEXT = CONFIG.get("MATCH_SCORE_TITLE_TEXT", "Match Score")
    MATCH_SCORE_TEXT = CONFIG.get("MATCH_SCORE_TEXT", "Allied {0} : Axis {1}")
    TIME_REMAINING_TEXT = CONFIG.get("TIME_REMAINING_TEXT", "Time Remaining")

    TOP_KILLERS = CONFIG["TOP_KILLERS"]
    TOP_RATIO = CONFIG["TOP_RATIO"]
    TOP_PERFORMANCE = CONFIG["TOP_PERFORMANCE"]
    TRY_HARDERS = CONFIG["TRY_HARDERS"]
    TOP_STAMINA = CONFIG["TOP_STAMINA"]
    TOP_KILL_STREAK = CONFIG["TOP_KILL_STREAK"]
    MOST_PATIENT = CONFIG["MOST_PATIENT"]
    I_NEVER_GIVE_UP = CONFIG["I_NEVER_GIVE_UP"]
    I_M_CLUMSY = CONFIG["I_M_CLUMSY"]
    I_NEED_GLASSES = CONFIG["I_NEED_GLASSES"]
    I_LOVE_VOTING = CONFIG["I_LOVE_VOTING"]
    WHAT_IS_A_BREAK = CONFIG["WHAT_IS_A_BREAK"]
    SURVIVORS = CONFIG["SURVIVORS"]
    U_R_STILL_A_MAN = CONFIG["U_R_STILL_A_MAN"]

    STATS_KEYS_TO_DISPLAY = CONFIG["STATS_TO_DISPLAY"]
except Exception as e:
    logger.exception(f"There's an error in your scorebot config: {repr(e)}")
    raise


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


def get_map_image(server_info):
    img = map_to_pict.get(
        server_info["current_map"]["just_name"], server_info["current_map"]["just_name"]
    )
    url = urljoin(SCOREBOARD_BASE_PATH, img)
    return url


def get_header_embed(public_info: PublicInfoType):
    elapsed_time_minutes = (
        datetime.datetime.now()
        - datetime.datetime.fromtimestamp(public_info["current_map"]["start"])
    ).total_seconds() / 60

    embed = discord.Embed(
        title=f"{public_info['name']}",
        description=f"**{public_info['current_map']['human_name']} - {ELAPSED_TIME}{round(elapsed_time_minutes)} min. - {public_info['player_count']}/{public_info['max_player_count']} {PLAYERS}**",
        color=13734400,
        timestamp=datetime.datetime.utcnow(),
        url=SCOREBOARD_PUBLIC_URL,
    )
    total_votes = public_info["vote_status"]["total_votes"]
    winning_map_votes = 0
    if len(public_info["vote_status"]["winning_maps"]) >= 1:
        winning_map_votes = public_info["vote_status"]["winning_maps"][0][1]

    embed.add_field(
        name=f"{NEXT_MAP_TEXT} {public_info['next_map']['human_name']}",
        value=f"{winning_map_votes}/{total_votes} {VOTE}",
    )

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name=f"{ALLIED_PLAYERS_TEXT}",
        value=f"{public_info['players']['allied']}",
        inline=True,
    )

    embed.add_field(
        name=f"{AXIS_PLAYERS_TEXT}",
        value=f"{public_info['players']['axis']}",
        inline=True,
    )

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    embed.add_field(
        name=f"{MATCH_SCORE_TITLE_TEXT}",
        value=MATCH_SCORE_TEXT.format(
            public_info["score"]["allied"], public_info["score"]["axis"]
        ),
        inline=True,
    )

    embed.add_field(
        name=f"{TIME_REMAINING_TEXT}",
        value=f"{public_info['raw_time_remaining']}",
        inline=True,
    )

    embed.set_author(
        name=AUTHOR_NAME,
        url=SCOREBOARD_PUBLIC_URL,
        icon_url=AUTHOR_ICON_URL,
    )
    embed.set_image(url=get_map_image(public_info))

    return embed


def escaped_name(stat):
    return (
        stat["player"]
        .replace("#", " ")
        .replace("[", "")
        .replace("]", "")
        .replace("```", "")
    )


def get_stat(
    stats, key, post_process=lambda v: v, limit=TOP_LIMIT, reverse=True, **kwargs
):
    stats = sorted(stats, key=lambda stat: stat[key], reverse=reverse)[:limit]

    return "```md\n%s\n```" % "\n".join(
        f"[#{rank}][{escaped_name(stat)}]: {post_process(stat[key])}"
        for rank, stat in enumerate(stats, start=1)
    )


def get_embeds(server_info, stats):
    embeds = []
    embeds.append(get_header_embed(server_info))

    stats_display = {
        "TOP_KILLERS": get_stat(stats, "kills"),
        "TOP_RATIO": get_stat(stats, "kill_death_ratio"),
        "TOP_PERFORMANCE": get_stat(stats, "kills_per_minute"),
        "TRY_HARDERS": get_stat(stats, "deaths_per_minute"),
        "TOP_STAMINA": get_stat(stats, "deaths"),
        "TOP_KILL_STREAK": get_stat(stats, "kills_streak"),
        "I_NEVER_GIVE_UP": get_stat(stats, "deaths_without_kill_streak"),
        "MOST_PATIENT": get_stat(stats, "deaths_by_tk"),
        "I_M_CLUMSY": get_stat(stats, "teamkills"),
        "I_NEED_GLASSES": get_stat(stats, "teamkills_streak"),
        "I_LOVE_VOTING": get_stat(stats, "nb_vote_started"),
        "WHAT_IS_A_BREAK": get_stat(
            stats, "time_seconds", post_process=lambda v: round(v / 60, 2)
        ),
        "SURVIVORS": get_stat(
            stats, "longest_life_secs", post_process=lambda v: round(v / 60, 2)
        ),
        "U_R_STILL_A_MAN": get_stat(
            stats,
            "shortest_life_secs",
            reverse=False,
        ),
    }
    stats_display = {
        CONFIG[k]: v for k, v in stats_display.items() if k in STATS_KEYS_TO_DISPLAY
    }

    current_embed = Embed(
        color=13734400,
    )
    if not stats:
        current_embed.add_field(
            name=NO_STATS_AVAILABLE, value=f"{FIND_PAST_STATS}{PAST_GAMES_URL}"
        )
        embeds.append(current_embed)
    else:
        for idx, (name, value) in enumerate(stats_display.items(), start=0):
            current_embed.add_field(name=name, value=value)
            if idx % 2:
                embeds.append(current_embed)
                current_embed = Embed(
                    color=13734400,
                )

    embeds[-1].add_field(
        name="\u200b", value=f"{ALL_STATS_TEXT}{SCOREBOARD_PUBLIC_URL}", inline=False
    )
    embeds[-1].set_footer(
        icon_url=FOOTER_ICON_URL, text="Community RCon based stats by Dr.WeeD"
    )
    print(embeds)
    return embeds


def get_stats():
    stats = requests.get(STATS_URL, verify=False).json()
    try:
        stats = stats["result"]["stats"]
    except KeyError:
        stats = stats["result"]["player_stats"]

    return stats


def cleanup_orphaned_messages(conn: Connection, server_number: int):
    conn.execute(
        "DELETE FROM stats_messages WHERE server_number = ? AND message_type = ? AND webhook = ?",
        (server_number, "live", WEBHOOK_URL),
    )
    conn.commit()


def run():
    try:
        path = os.getenv("DISCORD_BOT_DATA_PATH", "/data")
        path = pathlib.Path(path) / pathlib.Path("scorebot.db")
        conn = sqlite3.connect(str(path))
        server_number = int(os.getenv("SERVER_NUMBER", 0))
        # TODO handle webhook change
        # TODO handle invalid message id
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
        message_id = conn.execute(
            "SELECT message_id FROM stats_messages WHERE server_number = ? AND message_type = ? AND webhook = ?",
            (server_number, "live", WEBHOOK_URL),
        )
        message_id = message_id.fetchone()
        webhook = discord.Webhook.from_url(
            WEBHOOK_URL,
            adapter=discord.RequestsWebhookAdapter(),
        )
        try:
            public_info = requests.get(INFO_URL, verify=False).json()["result"]
        except ConnectionError as e:
            logger.error(f"Error accessing {INFO_URL}")
            raise

        stats = get_stats()

        if message_id:
            (message_id,) = message_id
            print("Resuming with message_id %s" % message_id)
        else:
            message = webhook.send(embeds=get_embeds(public_info, stats), wait=True)
            conn.execute(
                "INSERT INTO stats_messages VALUES (?, ?, ?, ?)",
                (server_number, "live", message.id, WEBHOOK_URL),
            )
            conn.commit()
            message_id = message.id
        while True:
            public_info = requests.get(INFO_URL, verify=False).json()["result"]
            stats = get_stats()
            try:
                webhook.edit_message(message_id, embeds=get_embeds(public_info, stats))
            except NotFound as ex:
                logger.exception(
                    "Message with ID in our records does not exist, cleaning up and restarting"
                )
                cleanup_orphaned_messages(conn, server_number)
                raise ex
            except (HTTPException, RequestException, ConnectionError):
                logger.exception("Temporary failure when trying to edit message")
                time.sleep(5)
            except Exception as e:
                logger.exception("Unable to edit message. Deleting record", e)
                cleanup_orphaned_messages(conn, server_number)
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
