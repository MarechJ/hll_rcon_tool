from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Iterable, Sequence

from humanize import naturaldelta, naturaltime
from sqlalchemy.orm import Session

import discord
from rcon.api_commands import RconAPI
from rcon.models import VipList, VipListRecord, enter_session
from rcon.seed_vip.models import (
    BaseCondition,
    Player,
    PlayTimeCondition,
    ServerPopulation,
    VipPlayer,
)
from rcon.types import GameStateType, GetPlayersType, VipIdWithExpirationType
from rcon.user_config.seed_vip import SeedVIPUserConfig
from rcon.vip import (
    add_record_to_vip_list,
    get_or_create_vip_list,
    get_vip_record,
    get_vip_status_for_player_ids,
)

logger = getLogger(__name__)


def filter_indefinite_vip_steam_ids(current_vips: dict[str, VipPlayer]) -> set[str]:
    """Return a set of steam IDs that have indefinite VIP status"""
    return {
        player_id
        for player_id, vip_player in current_vips.items()
        if has_indefinite_vip(vip_player)
    }


def has_indefinite_vip(player: VipPlayer | None) -> bool:
    """Return true if the player has an indefinite VIP status"""
    return player is not None and player.expiration_date is None


def all_met(conditions: Iterable[BaseCondition]) -> bool:
    return all(c.is_met() for c in conditions)


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


def is_seeded(config: SeedVIPUserConfig, gamestate: GameStateType) -> bool:
    """Return if the server has enough players to be out of seeding"""
    return (
        gamestate["num_allied_players"] >= config.requirements.max_allies
        and gamestate["num_axis_players"] >= config.requirements.max_axis
    )


def calc_vip_expiration_timestamp(
    config: SeedVIPUserConfig, current_expiration: datetime | None, from_time: datetime
) -> datetime:
    """Return the players new expiration date accounting for reward/existing timestamps"""
    if current_expiration is None:
        timestamp = from_time + config.reward.timeframe.as_timedelta
        return timestamp

    # If we are re-activating an old record (say someone seeded a week ago)
    # we have to reset their expiration time before we add on their newly
    # earned time; otherwise it is just going to add to an old date and still
    # be expired
    if current_expiration < from_time:
        current_expiration = from_time

    if config.reward.cumulative:
        return current_expiration + config.reward.timeframe.as_timedelta
    else:
        # Don't step on the old expiration if it's further in the future than the new one
        timestamp = from_time + config.reward.timeframe.as_timedelta
        if timestamp < current_expiration:
            return current_expiration
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
    vip_expiration: datetime | None,
    nice_time_delta: bool = True,
    nice_expiration_date: bool = True,
) -> str:
    if nice_time_delta:
        delta = naturaldelta(vip_reward)
    else:
        delta = vip_reward

    if vip_expiration is None:
        return message.format(vip_reward=delta, vip_expiration="Never")

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
    player_ids: Iterable[str],
):
    """Message each player and include their highest VIP expiration from all their records"""
    vip_records = get_vip_status_for_player_ids(player_ids=set(player_ids))
    for player_id in player_ids:
        if vip_records.get(player_id):
            formatted_message = format_player_message(
                message=message,
                vip_reward=config.reward.timeframe.as_timedelta,
                vip_expiration=vip_records[player_id]["expires_at"],
                nice_time_delta=config.nice_time_delta,
                nice_expiration_date=config.nice_expiration_date,
            )
        else:
            formatted_message = message

        if config.dry_run:
            logger.info(f"{config.dry_run=} messaging {player_id}: {formatted_message}")
        else:
            rcon.message_player(
                player_id=player_id,
                message=formatted_message,
            )


def reward_players(
    config: SeedVIPUserConfig,
    to_add_vip_steam_ids: set[str],
):
    """Create or edit VIP list records for all the players who earned VIP"""
    logger.info(f"Rewarding players with VIP {config.dry_run=}")
    logger.info(f"Total={len(to_add_vip_steam_ids)} {to_add_vip_steam_ids=}")

    timestamp = datetime.now(tz=timezone.utc)
    with enter_session() as sess:
        # People can misconfigure their config; or delete a list, but seeding
        # is pretty important; so make a new list if we don't find one
        vip_list: VipList = get_or_create_vip_list(
            sess=sess, vip_list_id=config.vip_list_id, name="Seed VIP"
        )
        record_lookup: dict[str, VipListRecord] = {
            r.player.player_id: r for r in vip_list.records
        }

        # Fix their config so that we don't keep creating new lists everytime
        # the service awards VIP if we made one
        if config.vip_list_id != vip_list.id:
            logger.info(
                f"Updating VIP list ID to {vip_list.id} from {config.vip_list_id}"
            )
            config.vip_list_id = vip_list.id
            config.save_to_db(config.model_dump())

        for player_id in to_add_vip_steam_ids:
            player_record_created = False
            if not config.dry_run:
                player_record = record_lookup.get(player_id)
                if player_record is None:
                    player_record = add_record_to_vip_list(
                        player_id=player_id,
                        vip_list_id=config.vip_list_id,
                        description=config.vip_record_description,
                    )
                    player_record_created = True
                    try:
                        player_record = get_vip_record(
                            sess=sess, record_id=player_record["id"]
                        )
                    except TypeError:
                        logger.error(
                            "Error while creating new VIP record for %s", player_id
                        )
                        continue

                if not player_record:
                    logger.error(
                        "Error while creating new VIP record for %s", player_id
                    )
                    continue

                # The record might be inactive; but we want to make sure they get VIP
                player_record.active = True
                # If the player record was created because it didn't exist; it has no expiration
                player_record.expires_at = calc_vip_expiration_timestamp(
                    config=config,
                    current_expiration=(
                        timestamp if player_record_created else player_record.expires_at
                    ),
                    from_time=timestamp,
                )

                logger.info(
                    f"{config.dry_run=} adding VIP to {player_id=} {player_record.to_dict(with_vip_list=False)}",
                )
            else:
                logger.info(
                    f"{config.dry_run=} adding VIP to {player_id=}",
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


def get_gamestate(rcon: RconAPI) -> GameStateType:
    return rcon.get_gamestate()


def get_vips(
    rcon: RconAPI,
) -> dict[str, VipPlayer]:
    raw_vips: list[VipIdWithExpirationType] = rcon.get_vip_ids()
    return {
        vip["player_id"]: VipPlayer(
            player=Player(
                player_id=vip["player_id"],
                name=vip["name"],
                current_playtime_seconds=0,
            ),
            expiration_date=vip["expires_at"],
        )
        for vip in raw_vips
    }
