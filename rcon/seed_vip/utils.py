from collections import defaultdict
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Iterable, Sequence

from humanize import naturaldelta, naturaltime

import discord
from rcon.api_commands import RconAPI
from rcon.seed_vip.models import (
    BaseCondition,
    GameState,
    Player,
    PlayerCountCondition,
    PlayTimeCondition,
    ServerPopulation,
    VipPlayer,
)
from rcon.types import GameStateType, GetPlayersType, VipIdType
from rcon.user_config.seed_vip import SeedVIPUserConfig
from rcon.utils import INDEFINITE_VIP_DATE

logger = getLogger(__name__)


def filter_indefinite_vip_steam_ids(current_vips: dict[str, VipPlayer]) -> set[str]:
    """Return a set of steam IDs that have indefinite VIP status"""
    return {
        player_id
        for player_id, vip_player in current_vips.items()
        if has_indefinite_vip(vip_player)
    }


def filter_online_players(
    vips: dict[str, VipPlayer], players: ServerPopulation
) -> dict[str, VipPlayer]:
    """Return a dictionary of players that are online"""
    return {
        player_id: vip_player
        for player_id, vip_player in vips.items()
        if player_id in players.players
    }


def has_indefinite_vip(player: VipPlayer | None) -> bool:
    """Return true if the player has an indefinite VIP status"""
    if player is None or player.expiration_date is None:
        return False
    expiration = player.expiration_date
    return expiration >= INDEFINITE_VIP_DATE


def all_met(conditions: Iterable[BaseCondition]) -> bool:
    return all(c.is_met() for c in conditions)


def check_population_conditions(
    config: SeedVIPUserConfig, gamestate: GameState
) -> bool:
    """Return if the current player count is within min/max players for seeding"""
    player_count_conditions = [
        PlayerCountCondition(
            faction="allies",
            min_players=config.requirements.min_allies,
            max_players=config.requirements.max_allies,
            current_players=gamestate.num_allied_players,
        ),
        PlayerCountCondition(
            faction="axis",
            min_players=config.requirements.min_axis,
            max_players=config.requirements.max_axis,
            current_players=gamestate.num_axis_players,
        ),
    ]

    logger.debug(
        f"{player_count_conditions[0]}={player_count_conditions[0].is_met()} {player_count_conditions[1]}={player_count_conditions[1].is_met()} breaking",
    )
    if not all_met(player_count_conditions):
        return False

    return True


def check_player_conditions(
    config: SeedVIPUserConfig, server_pop: ServerPopulation
) -> set[str]:
    """Return a set of steam IDs that meet seeding criteria"""
    return set(
        player.player_id
        for player in server_pop.players.values()
        if PlayTimeCondition(
            min_time_secs=int(config.requirements.minimum_play_time.total_seconds),
            current_time_secs=player.current_playtime_seconds,
        ).is_met()
    )


def is_seeded(config: SeedVIPUserConfig, gamestate: GameState) -> bool:
    """Return if the server has enough players to be out of seeding"""
    return (
        gamestate.num_allied_players >= config.requirements.max_allies
        and gamestate.num_axis_players >= config.requirements.max_axis
    )


def calc_vip_expiration_timestamp(
    config: SeedVIPUserConfig, expiration: datetime | None, from_time: datetime
) -> datetime:
    """Return the players new expiration date accounting for reward/existing timestamps"""
    if expiration is None:
        timestamp = from_time + config.reward.timeframe.as_timedelta
        return timestamp

    if config.reward.cumulative:
        return expiration + config.reward.timeframe.as_timedelta
    else:
        # Don't step on the old expiration if it's further in the future than the new one
        timestamp = from_time + config.reward.timeframe.as_timedelta
        if timestamp < expiration:
            return expiration
        else:
            return timestamp


def collect_steam_ids(
    config: SeedVIPUserConfig,
    players: ServerPopulation,
    cum_steam_ids: set[str],
) -> set[str]:
    player_conditions_steam_ids = check_player_conditions(
        config=config, server_pop=players
    )

    if config.requirements.online_when_seeded:
        cum_steam_ids = set(player_conditions_steam_ids)
    else:
        cum_steam_ids |= player_conditions_steam_ids

    return cum_steam_ids


def format_player_message(
    message: str,
    vip_reward: timedelta,
    vip_expiration: datetime,
    nice_time_delta: bool = True,
    nice_expiration_date: bool = True,
) -> str:
    if nice_time_delta:
        delta = naturaldelta(vip_reward)
    else:
        delta = vip_reward

    if nice_expiration_date:
        date = naturaltime(vip_expiration)
    else:
        date = vip_expiration.isoformat()

    return message.format(vip_reward=delta, vip_expiration=date)


def make_seed_announcement_embed(
    message: str | None,
    current_map: str,
    time_remaining: str,
    player_count_message: str,
    num_axis_players: int,
    num_allied_players: int,
) -> discord.Embed | None:
    if not message:
        return

    logger.debug(f"{num_allied_players=} {num_axis_players=}")

    embed = discord.Embed(title=message)
    embed.timestamp = datetime.now(tz=timezone.utc)
    embed.add_field(name="Current Map", value=current_map)
    embed.add_field(name="Time Remaining", value=time_remaining)
    embed.add_field(
        name="Players Per Team",
        value=player_count_message.format(
            num_allied_players=num_allied_players, num_axis_players=num_axis_players
        ),
    )

    return embed


def format_vip_reward_name(player_name: str, format_str):
    return format_str.format(player_name=player_name)


def should_announce_seeding_progress(
    player_buckets: list[int],
    total_players: int,
    prev_announced_bucket: int,
    next_player_bucket: int,
    last_bucket_announced: bool,
) -> bool:
    return (
        len(player_buckets) > 0
        and total_players > prev_announced_bucket
        and total_players >= next_player_bucket
        and not last_bucket_announced
    )


def message_players(
    rcon: RconAPI,
    config: SeedVIPUserConfig,
    message: str,
    steam_ids: Iterable[str],
    expiration_timestamps: defaultdict[str, datetime] | None,
):
    for steam_id in steam_ids:
        if expiration_timestamps:
            formatted_message = format_player_message(
                message=message,
                vip_reward=config.reward.timeframe.as_timedelta,
                vip_expiration=expiration_timestamps[steam_id],
                nice_time_delta=config.nice_time_delta,
                nice_expiration_date=config.nice_expiration_date,
            )
        else:
            formatted_message = message

        if config.dry_run:
            logger.info(f"{config.dry_run=} messaging {steam_id}: {formatted_message}")
        else:
            rcon.message_player(
                player_id=steam_id,
                message=formatted_message,
            )


def reward_players(
    rcon: RconAPI,
    config: SeedVIPUserConfig,
    to_add_vip_steam_ids: set[str],
    current_vips: dict[str, VipPlayer],
    players_lookup: dict[str, str],
    expiration_timestamps: defaultdict[str, datetime],
):
    logger.info(f"Rewarding players with VIP {config.dry_run=}")
    logger.info(f"Total={len(to_add_vip_steam_ids)} {to_add_vip_steam_ids=}")
    logger.info(f"Total={len(current_vips)=} {current_vips=}")
    for player_id in to_add_vip_steam_ids:
        player = current_vips.get(player_id)
        expiration_date = expiration_timestamps[player_id]

        if has_indefinite_vip(player):
            logger.info(
                f"{config.dry_run=} Skipping! pre-existing indefinite VIP for {player_id=} {player=} {vip_name=} {expiration_date=}"
            )
            continue

        vip_name = (
            if player
                player.player.name            
            else format_vip_reward_name(
                players_lookup.get(player_id, "No player name found"),
                format_str=config.reward.player_name_format_not_current_vip,
            )
        )

        if not config.dry_run:
            logger.info(
                f"{config.dry_run=} adding VIP to {player_id=} {player=} {vip_name=} {expiration_date=}",
            )
            rcon.add_vip(
                player_id=player_id,
                description=vip_name,
                expiration=expiration_date.isoformat(),
            )

        else:
            logger.info(
                f"{config.dry_run=} adding VIP to {player_id=} {player=} {vip_name=} {expiration_date=}",
            )


def get_next_player_bucket(
    player_buckets: Sequence[int],
    total_players: int,
) -> int | None:
    idx = None
    for idx, ele in enumerate(player_buckets):
        if ele > total_players:
            break

    try:
        if total_players > player_buckets[-1]:
            return player_buckets[-1]
        elif idx:
            return player_buckets[idx - 1]
    except IndexError:
        return None


def get_online_players(
    rcon: RconAPI,
) -> ServerPopulation:
    result: list[GetPlayersType] = rcon.get_players()
    players = {}
    for raw_player in result:
        name = raw_player["name"]
        player_id = player_id = raw_player["player_id"]
        if raw_player["profile"] is None:
            # Apparently CRCON will occasionally not return a player profile
            logger.debug(f"No CRCON profile, skipping {raw_player}")
            continue
        current_playtime_seconds = raw_player["profile"]["current_playtime_seconds"]  # type: ignore
        p = Player(
            name=name,
            player_id=player_id,
            current_playtime_seconds=current_playtime_seconds,
        )
        players[p.player_id] = p

    return ServerPopulation(players=players)


def get_gamestate(rcon: RconAPI) -> GameState:
    result: GameStateType = rcon.get_gamestate()
    return GameState.model_validate(result)


def get_vips(
    rcon: RconAPI,
) -> dict[str, VipPlayer]:
    raw_vips: list[VipIdType] = rcon.get_vip_ids()
    return {
        vip["player_id"]: VipPlayer(
            player=Player(
                player_id=vip["player_id"],
                name=vip["name"],
                current_playtime_seconds=0,
            ),
            expiration_date=vip["vip_expiration"],
        )
        for vip in raw_vips
    }
