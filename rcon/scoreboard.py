import pathlib
import sys
import time
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Generator, TypedDict
from urllib.parse import urljoin

from discord_webhook import DiscordEmbed, DiscordWebhook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from rcon.maps import UNKNOWN_MAP_NAME, FactionName, Layer, LayerType
from rcon.player_stats import get_cached_live_game_stats
from rcon.types import (
    STAT_DISPLAY_LOOKUP,
    GameStateType,
    PlayerStatsEnum,
    PlayerStatsType,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.scoreboard import (
    EMPTY_EMBED,
    HeaderGameStateEmbedEnum,
    ScoreboardUserConfig,
)
from rcon.utils import get_server_number
from rcon.webhook_service import (
    WebhookMessage,
    WebhookMessageType,
    WebhookType,
    enqueue_message,
)

if TYPE_CHECKING:
    from rcon.api_commands import RconAPI

from logging import getLogger

from sqlalchemy import Engine, create_engine, select

logger = getLogger(__name__)


HEADER_GAMESTATE = "HEADER_GAMESTATE"
MAP_ROTATION = "MAP_ROTATION"
PLAYER_STATS = "PLAYER_STATS"
MESSAGE_KEYS = (
    HEADER_GAMESTATE,
    MAP_ROTATION,
    PLAYER_STATS,
)
SERVER_NUMBER = int(get_server_number())

DB_PATH = pathlib.Path("./scoreboard.db")
ENGINE: Engine = create_engine(
    f"sqlite:///file:{DB_PATH}?mode=rwc&uri=true", echo=False
)


class Base(DeclarativeBase):
    pass


@contextmanager
def enter_session() -> Generator[Session, None, None]:
    with Session(bind=ENGINE) as session:
        session.begin()
        try:
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()


class Webhook(Base):
    __tablename__ = "webhooks"

    url: Mapped[str] = mapped_column(primary_key=True)
    header_gamestate: Mapped[str | None] = mapped_column(default=0)
    map_rotation: Mapped[str | None] = mapped_column(default=0)
    player_stats: Mapped[str | None] = mapped_column(default=0)
    server_number: Mapped[str] = mapped_column(default=SERVER_NUMBER, primary_key=True)

    def __repr__(self) -> str:
        return (
            f"Webhook(url={self.url} header_gamestate={self.header_gamestate}"
            f" map_rotation={self.map_rotation} player_stats={self.player_stats}"
            f" server_number={self.server_number})"
        )

    def __str__(self):
        return self.__repr__()


def get_set_wh_row(
    session: Session, webhook_url: str, server_number: int = SERVER_NUMBER
) -> Webhook:
    stmt = (
        select(Webhook)
        .filter(Webhook.url == webhook_url)
        .filter(Webhook.server_number == server_number)
    )
    res = session.scalars(stmt).one_or_none()

    if res is None:
        logger.warning(f"{server_number=} {webhook_url} not in database, adding it")
        res = Webhook(url=webhook_url)
        session.add(res)
        session.commit()
    return res


def save_message_id(session: Session, webhook_url: str, key: str, value: str):
    wh = get_set_wh_row(session=session, webhook_url=webhook_url)
    if key == HEADER_GAMESTATE:
        wh.header_gamestate = value
    if key == MAP_ROTATION:
        wh.map_rotation = value
    if key == PLAYER_STATS:
        wh.player_stats = value
    session.commit()


def guess_current_map_rotation_positions(
    rotation: list[Layer], current_map: LayerType, next_map: LayerType
) -> list[int]:
    """Estimate the index(es) of the current map in the rotation based off current/next map"""
    # As of U13 a map can be in a rotation more than once, but the index isn't
    # provided by RCON so we have to try to guess where we are in the rotation

    # TODO: what about single map rotations
    # TODO: use previous map to better estimate

    # Between rounds
    if current_map["id"] == UNKNOWN_MAP_NAME:
        return []

    raw_names = [map.id for map in rotation]

    # the current map is only in once then we know exactly where we are
    if raw_names.count(current_map["id"]) == 1:
        return [raw_names.index(current_map["id"])]

    # the current map is in more than once, we must estimate
    # if the next map is in only once then we know exactly where we are
    current_map_idxs = []
    for idx in [idx for idx, name in enumerate(raw_names) if name == next_map["id"]]:
        # if raw_names.count(next_map.raw_name) == 1:
        # next_map_idx = raw_names.index(next_map.raw_name)
        # current_map_idx = None

        # have to account for wrapping from the end to the start
        # current map is the end of the rotation
        if idx == 0:
            current_map_idx = len(raw_names) - 1
        # Somewhere besides the end of the rotation
        else:
            current_map_idx = idx - 1

        current_map_idxs.append(current_map_idx)
        # return [current_map_idx]

    return current_map_idxs

    # the current map is in more than once
    # and the next map is in multiple times so we can't determine where we are
    # return [idx for idx, name in enumerate(raw_names) if name == current_map.raw_name]


def guess_next_map_rotation_positions(
    current_map_positions: list[int], rotation: list[Layer]
) -> list[int]:
    """Estimate the index(es) of the next map in the rotation based off current/next map"""
    rotation_length = len(rotation)

    positions: list[int] = []
    for position in current_map_positions:
        # handle wrapping back to the start of the rotation
        if position == rotation_length - 1:
            positions.append(0)
        # otherwise the next map is immediately after the current map
        else:
            positions.append(position + 1)

    return positions


class TeamVIPCount(TypedDict):
    allies: int
    axis: int
    none: int


# TODO: move this to rcon
def get_vip_count_by_team(rcon_api: "RconAPI") -> TeamVIPCount:
    teams: TeamVIPCount = {"allies": 0, "axis": 0, "none": 0}

    team_view = rcon_api.get_team_view()
    for team in teams:
        try:
            for squad_key in team_view[team]["squads"].keys():
                for player in team_view[team]["squads"][squad_key]["players"]:
                    if player["is_vip"]:
                        teams[team] += 1
        except KeyError:
            continue

        commander = team_view[team]["commander"] or {}
        if commander.get("is_vip"):
            teams[team] += 1

    return teams


def get_map_image_url(config: ScoreboardUserConfig, gamestate: GameStateType):
    try:
        image_name = gamestate["current_map"]["image_name"]
        url = urljoin(str(config.public_scoreboard_url), f"maps/{image_name}")
    except (IndexError, KeyError, TypeError) as e:
        url = urljoin(
            str(config.public_scoreboard_url), f"maps/{UNKNOWN_MAP_NAME}.webp"
        )

    return url


def build_header_gamestate_embed(
    config: ScoreboardUserConfig, rcon_api: "RconAPI", short_name: str
) -> DiscordEmbed:
    """Build an embed for the header/gamestate message"""
    embed = DiscordEmbed()
    embed.set_url(str(config.public_scoreboard_url))

    gamestate: GameStateType = rcon_api.get_gamestate()
    vip_count_by_team = get_vip_count_by_team(rcon_api=rcon_api)

    if config.header_gamestate_include_server_name:
        server_name = rcon_api.get_name()
        embed.title = server_name

    for option in config.header_gamestate_embeds:
        name: str | None = None
        match option.value:

            case HeaderGameStateEmbedEnum.QUICK_CONNECT_URL:
                value = config.quick_connect_url
            case HeaderGameStateEmbedEnum.BATTLEMETRICS_URL:
                value = config.battlemetrics_url
            case HeaderGameStateEmbedEnum.RESERVED_VIP_SLOTS:
                value = rcon_api.get_vip_slots_num()
            case HeaderGameStateEmbedEnum.CURRENT_VIPS:
                value = rcon_api.get_vips_count()
            case HeaderGameStateEmbedEnum.NUM_ALLIED_PLAYERS:
                value = gamestate["num_allied_players"]
            case HeaderGameStateEmbedEnum.NUM_AXIS_PLAYERS:
                value = gamestate["num_axis_players"]
            case HeaderGameStateEmbedEnum.NUM_ALLIED_VIPS:
                value = vip_count_by_team["allies"]
            case HeaderGameStateEmbedEnum.NUM_AXIS_VIPS:
                value = vip_count_by_team["axis"]
            case HeaderGameStateEmbedEnum.SLOTS:
                slots = rcon_api.get_slots()
                value = f"{slots['current_players']}/{slots['max_players']}"
            case HeaderGameStateEmbedEnum.TIME_REMAINING:
                value = str(gamestate["time_remaining"])
            case HeaderGameStateEmbedEnum.CURRENT_MAP:
                value = str(gamestate["current_map"]["pretty_name"])
            case HeaderGameStateEmbedEnum.NEXT_MAP:
                value = str(gamestate["next_map"]["pretty_name"])
            case HeaderGameStateEmbedEnum.SCORE:
                if (
                    config.objective_score_format_ger_v_us
                    and gamestate["current_map"]["map"]["allies"]["name"]
                    == FactionName.US.value
                ):
                    format_str = config.objective_score_format_ger_v_us
                elif (
                    config.objective_score_format_ger_v_uk
                    and gamestate["current_map"]["map"]["allies"]["name"]
                    == FactionName.GB.value
                ):
                    format_str = config.objective_score_format_ger_v_uk
                elif (
                    config.objective_score_format_ger_v_sov
                    and gamestate["current_map"]["map"]["allies"]["name"]
                    == FactionName.RUS.value
                ):
                    format_str = config.objective_score_format_ger_v_sov
                else:
                    format_str = config.objective_score_format_generic
                value = format_str.format(
                    gamestate["allied_score"], gamestate["axis_score"]
                )
            # Not ideal but the match statement won't let us use the constant here
            case "\u200B":
                name = ""
                value = EMPTY_EMBED
            case _:
                raise ValueError(f"Unrecognized field: {option.value}")
        if name is None:
            name = option.name

        embed.add_embed_field(name=name, value=str(value), inline=option.inline)

    if config.show_map_image:
        url = get_map_image_url(config=config, gamestate=gamestate)
        embed.set_image(url=url)

    embed.set_footer(text=f"{short_name} - {config.footer_last_refreshed_text}")
    embed.set_timestamp(datetime.now(tz=timezone.utc))

    return embed


def build_map_rotation_embed(
    config: ScoreboardUserConfig, rcon_api: "RconAPI", short_name: str
) -> DiscordEmbed:
    """Build an embed for the map rotation message"""
    embed = DiscordEmbed()
    embed.set_url(str(config.public_scoreboard_url))

    rotation: list[Layer] = rcon_api.get_map_rotation()
    gamestate: GameStateType = rcon_api.get_gamestate()

    title = ""
    if config.map_rotation_include_server_name:
        server_name = rcon_api.get_name()
        title = server_name

    if title:
        embed.title = f"{title} - {config.map_rotation_title_text}"
    else:
        embed.title = config.map_rotation_title_text

    # shuffle_enabled
    current_map_positions: list[int] = guess_current_map_rotation_positions(
        rotation, gamestate["current_map"], gamestate["next_map"]
    )
    next_map_positions: list[int] = guess_next_map_rotation_positions(
        current_map_positions, rotation
    )

    description = []
    for idx, map_ in enumerate(rotation):
        if idx in current_map_positions:
            description.append(
                config.current_map_format.format(map_.pretty_name, idx + 1)
            )
        elif idx in next_map_positions:
            description.append(config.next_map_format.format(map_.pretty_name, idx + 1))
        else:
            description.append(
                config.other_map_format.format(map_.pretty_name, idx + 1)
            )

    if config.show_map_legend:
        description.append(config.map_legend)

    if description:
        embed.add_embed_field(name="", value="\n".join(description))

    embed.set_footer(text=f"{short_name} - {config.footer_last_refreshed_text}")
    embed.set_timestamp(datetime.now(tz=timezone.utc))
    return embed


def build_player_stats_embed(
    config: ScoreboardUserConfig, rcon_api: "RconAPI", short_name: str
):
    player_stats: list[PlayerStatsType] = get_cached_live_game_stats()["stats"]

    embed = DiscordEmbed()
    embed.set_url(str(config.public_scoreboard_url))

    title = ""
    if config.player_stats_include_server_name:
        server_name = rcon_api.get_name()
        title = server_name

    if title:
        embed.title = f"{title} - {config.player_stats_title_text}"
    else:
        embed.title = config.player_stats_title_text

    reverse_sort = defaultdict(lambda: True)
    reverse_sort[PlayerStatsEnum.SHORTEST_LIFE_SECS] = False

    for option in config.player_stat_embeds:
        if option.value == EMPTY_EMBED:
            embed.add_embed_field(name="", value=option.value, inline=option.inline)
        else:
            stat = STAT_DISPLAY_LOOKUP[PlayerStatsEnum[option.value.upper()]]
            stats: list[PlayerStatsType] = sorted(
                player_stats,
                key=lambda player_stat: player_stat[stat],
                reverse=reverse_sort[PlayerStatsEnum(stat)],
            )[: config.player_stats_num_to_display]
            stats_strings = [
                f"[#{idx+1}][{player_stat['player']}]: {player_stat[stat]}"
                for idx, player_stat in enumerate(stats)
            ]
            embed.add_embed_field(
                name=option.name,
                value="```md\n{content}\n```".format(content="\n".join(stats_strings)),
                inline=option.inline,
            )

    embed.set_footer(text=f"{short_name} - {config.footer_last_refreshed_text}")
    embed.set_timestamp(datetime.now(tz=timezone.utc))
    return embed


def create_initial_message(url: str, embed: DiscordEmbed) -> str:
    wh = DiscordWebhook(url=url)
    wh.add_embed(embed)
    wh.execute()
    return wh.message_id


def send_message(
    session: Session,
    wh: DiscordWebhook,
    embed: DiscordEmbed,
    message_id: str | None,
    key: str,
):
    wh.message_id = message_id
    wh.add_embed(embed)
    # When a message doesn't exist; or we have no message IDs we have to
    # create/send one; persist the ID and then enqueue future updates
    # through the webhook service
    if not message_id or not wh.message_exists():
        message_id = create_initial_message(url=wh.url, embed=embed)
        save_message_id(
            session=session,
            webhook_url=wh.url,
            key=key,
            value=message_id,
        )
    else:
        logger.info(f"enqueing {wh.message_id=} {key=}")
        enqueue_message(
            message=WebhookMessage(
                discardable=True,
                edit=True,
                webhook_type=WebhookType.DISCORD,
                message_type=WebhookMessageType.SCOREBOARD,
                server_number=SERVER_NUMBER,
                payload=wh.json,
            )
        )


def run():
    # Avoid circular imports
    from rcon.api_commands import get_rcon_api

    config = ScoreboardUserConfig.load_from_db()
    rcon_api = get_rcon_api()

    try:
        if config.public_scoreboard_url is None:
            logger.error(
                "Your Public Scoreboard URL is not configured, set it and restart the Scoreboard service."
            )
            sys.exit(-1)

        if not config.hooks:
            logger.error(
                "You do not have any Discord webhooks configured, set some and restart the Scoreboard service."
            )
            sys.exit(-1)

        last_updated_header_gamestate: datetime | None = None
        last_updated_map_rotation: datetime | None = None
        last_updated_player_stats: datetime | None = None
        while True:
            timestamp = datetime.now()
            config = ScoreboardUserConfig.load_from_db()
            server_config = RconServerSettingsUserConfig.load_from_db()

            for webhook in config.hooks:
                url = str(webhook.url)

                with enter_session() as session:
                    message_ids = get_set_wh_row(session=session, webhook_url=url)
                    for key in MESSAGE_KEYS:
                        if key == HEADER_GAMESTATE and config.header_gamestate_enabled:
                            if (
                                last_updated_header_gamestate
                                and (
                                    timestamp - last_updated_header_gamestate
                                ).total_seconds()
                                < config.header_gamestate_time_between_refreshes
                            ):
                                continue
                            last_updated_header_gamestate = timestamp
                            wh = DiscordWebhook(url=url)
                            embed = build_header_gamestate_embed(
                                config=config,
                                rcon_api=rcon_api,
                                short_name=server_config.short_name,
                            )
                            send_message(
                                session=session,
                                wh=wh,
                                embed=embed,
                                message_id=message_ids.header_gamestate,
                                key=key,
                            )

                        if key == MAP_ROTATION and config.map_rotation_enabled:
                            if (
                                last_updated_map_rotation
                                and (
                                    timestamp - last_updated_map_rotation
                                ).total_seconds()
                                < config.map_rotation_time_between_refreshes
                            ):
                                continue
                            last_updated_map_rotation = timestamp
                            wh = DiscordWebhook(url=url)
                            embed = build_map_rotation_embed(
                                config=config,
                                rcon_api=rcon_api,
                                short_name=server_config.short_name,
                            )
                            send_message(
                                session=session,
                                wh=wh,
                                embed=embed,
                                message_id=message_ids.map_rotation,
                                key=key,
                            )

                        if key == PLAYER_STATS and config.player_stats_enabled:
                            if (
                                last_updated_player_stats
                                and (
                                    timestamp - last_updated_player_stats
                                ).total_seconds()
                                < config.player_stats_time_between_refreshes
                            ):
                                continue
                            last_updated_player_stats = timestamp
                            wh = DiscordWebhook(url=url)
                            embed = build_player_stats_embed(
                                config=config,
                                rcon_api=rcon_api,
                                short_name=server_config.short_name,
                            )
                            send_message(
                                session=session,
                                wh=wh,
                                embed=embed,
                                message_id=message_ids.player_stats,
                                key=key,
                            )
                sleep_time = min(
                    config.header_gamestate_time_between_refreshes,
                    config.map_rotation_time_between_refreshes,
                    config.player_stats_time_between_refreshes,
                )
                time.sleep(sleep_time)
    except Exception as e:
        logger.exception("The bot stopped", e)
        raise


if __name__ == "__main__":
    try:
        logger.info("Attempting to start scorebot")
        Base.metadata.create_all(ENGINE)
        run()
    except Exception as e:
        logger.exception(e)
        raise
