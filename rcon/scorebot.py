import datetime
import logging
import os
import pathlib
import sys
import time
from typing import Callable
from urllib.parse import urljoin

import requests
from requests.exceptions import ConnectionError, RequestException

import discord
from discord.embeds import Embed
from discord.errors import HTTPException, NotFound
from rcon.scoreboard import STAT_DISPLAY_LOOKUP, get_stat, get_stat_post_processor
from rcon.user_config.scorebot import ScorebotUserConfig, StatTypes
from rcon.utils import UNKNOWN_MAP_NAME, get_server_number
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine, select
from typing import Generator
from rcon.types import PublicInfoType, PlayerStatsType
from contextlib import contextmanager

# TODO: This env var isn't actually exposed anywhere
root_path = os.getenv("DISCORD_BOT_DATA_PATH", "/data")
full_path = pathlib.Path(root_path) / pathlib.Path("scorebot.db")

logger = logging.getLogger("rcon")

engine = create_engine(f"sqlite:///file:{full_path}?mode=rwc&uri=true", echo=False)


@contextmanager
def enter_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        session.begin()
        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()


class Base(DeclarativeBase):
    pass


class ScorebotMessage(Base):
    __tablename__ = "stats_messages"

    server_number: Mapped[int] = mapped_column(primary_key=True)
    message_type: Mapped[str] = mapped_column(default="live", primary_key=True)
    message_id: Mapped[int] = mapped_column(primary_key=True)
    webhook: Mapped[str] = mapped_column(primary_key=True)


def fetch_existing(
    session: Session, server_number: str, webhook_url: str
) -> ScorebotMessage | None:
    stmt = (
        select(ScorebotMessage)
        .where(ScorebotMessage.server_number == server_number)
        .where(ScorebotMessage.webhook == webhook_url)
    )
    return session.scalars(stmt).one_or_none()


def cleanup_orphaned_messages(
    session: Session, server_number: int, webhook_url: str
) -> None:
    stmt = (
        select(ScorebotMessage)
        .where(ScorebotMessage.server_number == server_number)
        .where(ScorebotMessage.webhook == webhook_url)
    )
    res = session.scalars(stmt).one_or_none()

    if res:
        session.delete(res)


# TODO: Need to update this when we get Abu style maps in
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


# TODO: Update this when we get improved map types
def get_map_image(server_info: PublicInfoType, config: ScorebotUserConfig):
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


def format_stat(
    stats,
    key: StatTypes,
    post_process: Callable | None = None,
):
    if post_process is None:
        post_process = get_stat_post_processor(key)

    return "```md\n%s\n```" % "\n".join(
        f"[#{rank}][{escaped_name(stat)}]: {post_process(stat[STAT_DISPLAY_LOOKUP[key]])}"
        for rank, stat in enumerate(stats, start=1)
    )


def get_embeds(server_info, stats, config: ScorebotUserConfig):
    embeds = []
    embeds.append(get_header_embed(server_info, config))

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
            stat_values = get_stat(
                stats,
                key=stat_display.type,
                limit=config.top_limit,
            )
            current_embed.add_field(
                name=stat_display.display_format,
                value=format_stat(stat_values, key=stat_display.type),
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


def get_stats(stats_url: str) -> list[PlayerStatsType]:
    stats = requests.get(stats_url, verify=False).json()
    try:
        stats = stats["result"]["stats"]
    except KeyError:
        stats = stats["result"]["player_stats"]

    return stats


def send_or_edit_message(
    session: Session,
    webhook: discord.SyncWebhook,
    embeds: list[discord.Embed],
    server_number: int,
    message_id: int | None = None,
    edit: bool = True,
):

    try:
        # Force creation of a new message if message ID isn't set
        if not edit or message_id is None:
            logger.info(f"Creating a new scorebot message")
            message = webhook.send(embeds=embeds, wait=True)
            return message.id
        else:
            webhook.edit_message(message_id, embeds=embeds)
            return message_id
    except NotFound as ex:
        logger.error(
            "Message with ID: %s in our records does not exist",
            message_id,
        )
        cleanup_orphaned_messages(
            session=session,
            server_number=server_number,
            webhook_url=webhook.url,
        )
        return None
    except (HTTPException, RequestException, ConnectionError):
        logger.exception(
            "Temporary failure when trying to edit message ID: %s", message_id
        )
    except Exception as e:
        logger.exception("Unable to edit message. Deleting record", e)
        cleanup_orphaned_messages(
            session=session,
            server_number=server_number,
            webhook_url=webhook.url,
        )
        return None


def run():
    config = ScorebotUserConfig.load_from_db()
    try:
        server_number = get_server_number()
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
            public_info: PublicInfoType = requests.get(
                config.info_url, verify=False
            ).json()["result"]
        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                f"Bad result (invalid JSON) from {config.info_url}, check your CRCON backend status"
            )
            sys.exit(-1)
        except ConnectionError as e:
            logger.error(f"Error accessing {config.info_url}")
            raise

        stats = get_stats(config.stats_url)
        message_id: int | None = None
        seen_messages: set[int] = set()
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
                with enter_session() as session:
                    db_message = fetch_existing(
                        session=session,
                        server_number=server_number,
                        webhook_url=webhook.url,
                    )
                    embeds = get_embeds(public_info, stats, config)
                    if db_message:
                        message_id = db_message.message_id
                        if message_id not in seen_messages:
                            logger.info("Resuming with message_id %s" % message_id)
                            seen_messages.add(message_id)
                        message_id = send_or_edit_message(
                            session=session,
                            webhook=webhook,
                            embeds=embeds,
                            server_number=server_number,
                            message_id=message_id,
                            edit=True,
                        )
                    else:
                        message_id = send_or_edit_message(
                            session=session,
                            webhook=webhook,
                            embeds=embeds,
                            server_number=server_number,
                            message_id=None,
                            edit=False,
                        )
                        if message_id:
                            db_message = ScorebotMessage(
                                server_number=server_number,
                                message_id=message_id,
                                webhook=webhook.url,
                            )
                            session.add(db_message)

            time.sleep(config.refresh_time_secs)
    except Exception as e:
        logger.exception("The bot stopped", e)
        raise


if __name__ == "__main__":
    try:
        logger.info("Attempting to start scorebot")
        Base.metadata.create_all(engine)
        run()
    except Exception as e:
        logger.exception(e)
        raise
