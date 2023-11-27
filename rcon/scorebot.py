import datetime
import logging
import os
import pathlib
import sqlite3
import sys
import time
from collections import defaultdict
from sqlite3 import Connection
from typing import Callable, TypedDict
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError, RequestException

import discord
from discord.embeds import Embed
from discord.errors import HTTPException, NotFound
from rcon.cache_utils import ttl_cache
from rcon.user_config.scorebot import ScorebotUserConfig, StatTypes
from rcon.utils import UNKNOWN_MAP_NAME


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

map_to_pict = {
    "carentan": "maps/carentan.webp",
    "carentan_night": "maps/carentan-night.webp",
    "driel": "maps/driel.webp",
    "driel_night": "maps/driel-night.webp",
    "elalamein": "maps/elalamein.webp",
    "elalamein_night": "maps/elalamein-night.webp",
    "foy": "maps/foy.webp",
    "foy_night": "maps/foy-night.webp",
    "hill400": "maps/hill400.webp",
    "hill400_night": "maps/hill400-night.webp",
    "hurtgenforest": "maps/hurtgen.webp",
    "hurtgenforest_night": "maps/hurtgen-night.webp",
    "kharkov": "maps/kharkov.webp",
    "kharkov_night": "maps/kharkov-night.webp",
    "kursk": "maps/kursk.webp",
    "kursk_night": "maps/kursk-night.webp",
    "omahabeach": "maps/omaha.webp",
    "omahabeach_night": "maps/omaha-night.webp",
    "purpleheartlane": "maps/phl.webp",
    "purpleheartlane_night": "maps/phl-night.webp",
    "stalingrad": "maps/stalingrad.webp",
    "stalingrad_night": "maps/stalingrad-night.webp",
    "stmariedumont": "maps/smdm.webp",
    "stmariedumont_night": "maps/smdm-night.webp",
    "stmereeglise": "maps/sme.webp",
    "stmereeglise_night": "maps/sme-night.webp",
    "utahbeach": "maps/utah.webp",
    "utahbeach_night": "maps/utah-night.webp",
    UNKNOWN_MAP_NAME: "maps/unknown.webp",
}


def get_map_image(server_info, config: ScorebotUserConfig):
    map_name: str = server_info["current_map"]["name"]

    try:
        base_map_name, _ = map_name.split("_", maxsplit=1)
    except ValueError:
        base_map_name = map_name

    if "night" in map_name.lower():
        base_map_name = base_map_name + "_night"

    img = map_to_pict.get(base_map_name, UNKNOWN_MAP_NAME)
    url = urljoin(str(config.base_scoreboard_url), img)
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
        url=str(config.base_scoreboard_url),
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
        url=str(config.base_scoreboard_url),
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


def get_stat(
    stats,
    key: str,
    limit: int,
    post_process: Callable | None = None,
    reverse=True,
    **kwargs,
):
    if post_process is None:
        post_process = lambda v: v
    stats = sorted(stats, key=lambda stat: stat[key], reverse=reverse)[:limit]

    return "```md\n%s\n```" % "\n".join(
        f"[#{rank}][{escaped_name(stat)}]: {post_process(stat[key])}"
        for rank, stat in enumerate(stats, start=1)
    )


def get_embeds(server_info, stats, config: ScorebotUserConfig):
    embeds = []
    embeds.append(get_header_embed(server_info, config))

    stat_display_lookup = {
        StatTypes.top_killers: "kills",
        StatTypes.top_ratio: "kill_death_ratio",
        StatTypes.top_performance: "kills_per_minute",
        StatTypes.try_harders: "deaths_per_minute",
        StatTypes.top_stamina: "deaths",
        StatTypes.top_kill_streak: "kills_streak",
        StatTypes.i_never_give_up: "deaths_without_kill_streak",
        StatTypes.most_patient: "deaths_by_tk",
        StatTypes.im_clumsy: "teamkills",
        StatTypes.i_need_glasses: "teamkills_streak",
        StatTypes.i_love_voting: "nb_vote_started",
        StatTypes.what_is_a_break: "time_seconds",
        StatTypes.survivors: "longest_life_secs",
        StatTypes.u_r_still_a_man: "shortest_life_secs",
    }

    stat_display_lambda_lookup = {}
    stat_display_lambda_lookup[StatTypes.what_is_a_break] = lambda v: round(v / 60, 2)
    stat_display_lambda_lookup[StatTypes.survivors] = lambda v: round(v / 60, 2)

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
            if stat_display.type in (StatTypes.u_r_still_a_man,):
                reverse = False
            else:
                reverse = True

            current_embed.add_field(
                name=stat_display.display_format,
                value=get_stat(
                    stats,
                    stat_display_lookup[stat_display.type],
                    config.top_limit,
                    post_process=stat_display_lambda_lookup.get(stat_display.type),
                    reverse=reverse,
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
    config = ScorebotUserConfig.load_from_db()
    try:
        path = os.getenv("DISCORD_BOT_DATA_PATH", "/data")
        path = pathlib.Path(path) / pathlib.Path("scorebot.db")
        conn = sqlite3.connect(str(path))
        server_number = int(os.getenv("SERVER_NUMBER", 0))
        create_table(conn)
        # TODO handle webhook change
        # TODO handle invalid message id

        webhooks = [
            discord.SyncWebhook.from_url(
                webhook_url,
            )
            for webhook_url in config.webhook_urls
        ]

        if config.base_api_url is None:
            logger.error("Your scorebot API URL is not configured, exiting")
            sys.exit(-1)

        if config.base_scoreboard_url is None:
            logger.error("Your scorebot Scoreboard URL is not configured, exiting")
            sys.exit(-1)

        try:
            public_info = requests.get(config.info_url, verify=False).json()["result"]
        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                f"Bad result (invalid JSON) from {config.info_url}, check your CRCON backend status"
            )
            sys.exit(-1)
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
            config = ScorebotUserConfig.load_from_db()
            try:
                public_info = requests.get(config.info_url, verify=False).json()[
                    "result"
                ]
            except requests.exceptions.JSONDecodeError:
                logger.error(
                    f"Bad result from (invalid JSON) {config.info_url}, check your CRCON backend status"
                )
                sys.exit(-1)

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
                logger.info(f"sleeping for {config.refresh_time_secs} seconds")
                time.sleep(config.refresh_time_secs)
    except Exception as e:
        logger.exception("The bot stopped", e)
        raise


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.exception(e)
        raise
