import logging
import pickle
import random
from datetime import datetime, timezone
from itertools import cycle

import redis

from rcon.discord import send_to_discord_audit
from rcon.recorded_commands import RecordedRcon
from rcon.team_shuffle.constants import (
    ALLIED_TEAM,
    AXIS_TEAM,
    EMPTY_TEAM,
    INVALID_SWAP_TYPE_ERROR_MSG,
    REDIS_PLAYER_KEY,
    REDIS_TEAM_SHUFFLE_KEY,
    SWAP_TYPE_EVEN_TEAMS,
    SWAP_TYPES,
    UNABLE_TO_SET_REDIS_KEY_ERROR_MSG,
)
from rcon.team_shuffle.models import SwapRateLimitError, TeamShuffleConfig
from rcon.types import TeamViewPlayerType, TeamViewType

logger = logging.getLogger("rcon.team_shuffle")


def get_team_player_count(team_view: TeamViewType, team_name: str) -> int:
    """Return the number of players on the specified team."""
    player_count: int = 0

    # Relying on well formed team_views here, if we don't have one better to fail early on a key error
    if team_view.get(team_name, None):
        player_count = team_view[team_name]["count"]

    return player_count


def get_players_on_team(
    team_view: TeamViewType, team_name: str
) -> list[TeamViewPlayerType]:
    """Collect all the players on a specific team from the given team view."""
    team_players: list[TeamViewPlayerType] = []

    # Relying on well formed team_views here, if we don't have one better to fail early on a key error
    if team := team_view.get(team_name, None):
        for squad in team["squads"].values():
            for player in squad["players"]:
                team_players.append(player)

        if team.get("commander", None):
            team_players.append(team["commander"])

    return team_players


def check_swap_rate_limit(
    redis_store: redis.StrictRedis,
    rate_limit: int,
    timestamp: datetime | None = None,
) -> None:
    """Raise a SwapRateLimitError if ran too recently or set the new run timestamp."""
    last_swap_timestamp = get_balance_timestamp(redis_store)
    if (
        last_swap_timestamp
        and (
            delta := (datetime.now(timezone.utc) - last_swap_timestamp)
        ).total_seconds()
        < rate_limit
    ):
        raise SwapRateLimitError(
            f"Balance/Shuffle attempted {round(delta.total_seconds(), 1)} seconds ago, configured limit is {rate_limit} seconds."
        )

    set_balance_timestamp(redis_store, timestamp)


def set_balance_timestamp(
    redis_store: redis.StrictRedis,
    timestamp: datetime | None = None,
    redis_key: str = REDIS_TEAM_SHUFFLE_KEY,
) -> None:
    """Set the UTC timestamp of the shuffle/balance attempt."""
    time_stamp = timestamp or datetime.now(timezone.utc)

    if not redis_store.set(redis_key, pickle.dumps(time_stamp)):
        raise redis.RedisError(UNABLE_TO_SET_REDIS_KEY_ERROR_MSG.format(redis_key))


def get_balance_timestamp(
    redis_store: redis.StrictRedis, redis_key: str = REDIS_TEAM_SHUFFLE_KEY
) -> datetime | None:
    """Return the UTC timestamp of the last shuffle/balance or None."""

    last_raw_timestamp = redis_store.get(redis_key)
    last_timestamp: datetime | None = None
    if last_raw_timestamp:
        last_timestamp = pickle.loads(last_raw_timestamp)
        last_timestamp.replace(tzinfo=timezone.utc)

    return last_timestamp


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def set_player_swap_timestamp(
    redis_store: redis.StrictRedis,
    timestamp: datetime | None = None,
    *,
    steam_id_64: str,
    swap_type: str,
) -> None:
    """Set the timestamp for the players balance (not shuffle) or current time by default."""
    if swap_type not in SWAP_TYPES:
        raise ValueError(INVALID_SWAP_TYPE_ERROR_MSG.format(swap_type))

    redis_key = REDIS_PLAYER_KEY.format(steam_id_64)
    timestamp = timestamp or datetime.now(timezone.utc)

    if not redis_store.set(redis_key, pickle.dumps(timestamp)):
        raise redis.RedisError(UNABLE_TO_SET_REDIS_KEY_ERROR_MSG.format(redis_key))


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def get_player_last_swap_timestamp(
    redis_store: redis.StrictRedis, *, steam_id_64: str, swap_type: str
) -> datetime:
    """Get the timestamp of the players last balance (not shuffle)."""
    # Blatantly ripped off from squad_automod.watch_state

    if swap_type not in SWAP_TYPES:
        raise ValueError(INVALID_SWAP_TYPE_ERROR_MSG.format(swap_type))

    # TODO: Change this to a redis hash or something so we don't pollute the store with a ton of key/value pairs
    redis_key = REDIS_PLAYER_KEY.format(steam_id_64)

    # Use January 1st of year 1 as a sentinel date if this player hasn't been swapped before
    impossibly_old_datetime = datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc)

    # TODO: Distinguish between failed gets and the player not existing in redis?
    last_swap_raw = redis_store.get(redis_key)
    if last_swap_raw:
        last_swap: datetime = pickle.loads(last_swap_raw)
        last_swap = last_swap.replace(tzinfo=timezone.utc)
    else:
        # Haven't seen this player before, store the sentinel value
        set_player_swap_timestamp(
            redis_store,
            timestamp=impossibly_old_datetime,
            steam_id_64=steam_id_64,
            swap_type=swap_type,
        )
        last_swap = impossibly_old_datetime
        # last_swap.replace(t zinfo=timezone.utc)

    return last_swap


def select_players_randomly(
    players: list[TeamViewPlayerType], num_to_select: int
) -> list[TeamViewPlayerType]:
    """Select up to num_to_select players randomly from the given list of players"""
    if len(players) == 0:
        return []

    shuffled_players: list[TeamViewPlayerType] = players[:]
    random.shuffle(shuffled_players)

    # If we don't have enough possible players to swap, use as many as possible
    if num_to_select > len(shuffled_players):
        return shuffled_players

    # Otherwise grab only the desired number of players
    return shuffled_players[0:num_to_select]


def get_player_session(player: TeamViewPlayerType, most_recent: bool) -> datetime:
    """Always include a player if their session information is missing."""
    try:
        # Session time stamps are stored as UTC but this has to be forced when parsing the date
        session_timestamp = player["profile"]["sessions"][0]["start"]
        return session_timestamp.replace(tzinfo=timezone.utc)
    except (KeyError, IndexError):
        # If we're missing session info then include the player
        if most_recent:
            return datetime.now(timezone.utc)
        else:
            return datetime(1, 1, 1, 0, 0, 0, 0, timezone.utc)


def swap_players(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    config: TeamShuffleConfig,
    players_to_swap: list[TeamViewPlayerType],
    swap_type: str,
    swap_on_death: bool = False,
    from_team: str | None = None,
    to_team: str | None = None,
    swap_message: str = "",
) -> tuple[list[TeamViewPlayerType], list[TeamViewPlayerType]]:
    """Swap players and handle logging."""

    swapped_axis_players: list[TeamViewPlayerType] = []
    swapped_allied_players: list[TeamViewPlayerType] = []

    switch_type: str
    if swap_on_death:
        switch_function = rcon_hook.do_switch_player_on_death
        switch_type = config.swap_on_death_description
    else:
        switch_function = rcon_hook.do_switch_player_now
        switch_type = config.swap_immediately_description

    for player in players_to_swap:
        rcon_hook.do_message_player(
            steam_id_64=player["steam_id_64"],
            message=swap_message,
            by=config.discord_audit_service_name,
            save_message=False,
        )
        # this function has a unused 'by' argument
        result = switch_function(player["name"], None)
        if result == "SUCCESS":
            set_player_swap_timestamp(
                redis_store,
                steam_id_64=player["steam_id_64"],
                swap_type=swap_type,
            )

            destination_team: str = ALLIED_TEAM
            if player["team"] == ALLIED_TEAM:
                swapped_allied_players.append(player)
                destination_team = AXIS_TEAM
            elif player["team"] == AXIS_TEAM:
                swapped_axis_players.append(player)

            if not from_team:
                from_team = player["team"]

            if not to_team:
                to_team = destination_team

            if swap_type == SWAP_TYPE_EVEN_TEAMS:
                message = config.even_teams_logger_message
            else:
                message = config.shuffle_teams_logger_message

            message = message.replace("{player_name}", player["name"])
            message = message.replace("{steam_id}", player["name"])
            message = message.replace("{from_team}", from_team)
            message = message.replace("{to_team}", to_team)
            message = message.replace("{switch_type}", switch_type)

            # When called with teamless players it's called one player at a time
            # When called for a list of players with more than one player we have to
            # reset these or these are stale values from the previous loop
            from_team = None
            to_team = None

            logger.info(message)
            if config.discord_audit_swaps:
                audit(
                    config.discord_webhook_url,
                    message,
                    by=config.discord_audit_service_name,
                )
        else:
            message = config.failed_swap_logger_message
            message = message.replace("{player_name}", player["name"])
            message = message.replace("{steam_id}", player["name"])

            logger.error(message)
            if config.discord_audit_swaps:
                audit(
                    config.discord_webhook_url,
                    message,
                    by=config.discord_audit_service_name,
                )

        # time.sleep(RCON_TEAM_SWAP_DELAY_MS / 1000)

    return swapped_axis_players, swapped_allied_players


def swap_teamless_players(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    config: TeamShuffleConfig,
    teamless_players_to_swap: list[TeamViewPlayerType],
    swap_type: str,
    swap_on_death: bool = False,
    swap_message: str = "",
) -> None:
    """Handle swapping teamless players between teams evenly."""

    # Distribute teamless players to each team, choosing which team to start with at random
    # Whether or not to include teamless players is determined when collecting those players
    alternating_teams: tuple[str, str] = (AXIS_TEAM, ALLIED_TEAM)
    if random.choice(alternating_teams) == ALLIED_TEAM:
        alternating_teams = (ALLIED_TEAM, AXIS_TEAM)

    for player, team in zip(teamless_players_to_swap, cycle(alternating_teams)):
        swap_players(
            rcon_hook,
            redis_store,
            config,
            [player],
            swap_type,
            swap_on_death,
            from_team=EMPTY_TEAM,
            to_team=ALLIED_TEAM,
            swap_message=swap_message,
        )
        # When swapping a teamless player, RCON defaults to putting them on the Allied team
        # and they have to be swapped twice to get to the Axis team
        if team == AXIS_TEAM:
            swap_players(
                rcon_hook,
                redis_store,
                config,
                [player],
                swap_type,
                swap_on_death,
                from_team=ALLIED_TEAM,
                to_team=AXIS_TEAM,
                swap_message=swap_message,
            )


def audit(discord_webhook_url: str | None, message: str, by: str) -> None:
    """Send message to the given Discord webhook."""
    webhook_url = None
    if discord_webhook_url is not None and discord_webhook_url != "":
        webhook_url = discord_webhook_url
    send_to_discord_audit(message, by=by, webhookurl=webhook_url, silent=False)
