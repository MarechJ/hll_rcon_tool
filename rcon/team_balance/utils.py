import logging
import pickle
import random
from datetime import datetime, timezone
from itertools import cycle
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

import redis

from rcon.discord import send_to_discord_audit
from rcon.recorded_commands import RecordedRcon
from rcon.team_balance.constants import (
    ALLIED_TEAM,
    AXIS_TEAM,
    BALANCE_RATE_LIMIT_EXCEEDED_ERROR_MSG,
    DISCORD_BALANCE_SHUFFLE_WEBHOOK,
    EMPTY_TEAM,
    INVALID_SWAP_TYPE_ERROR_MSG,
    PLAYER_BALANCE_SWAP_MSG,
    PLAYER_SHUFFLE_SWAP_MSG,
    RCON_SWAP_FAILED_ERROR_MSG,
    RCON_TEAM_SWAP_DELAY_MS,
    REDIS_BALANCE_KEY,
    REDIS_PLAYER_KEY,
    SWAP_IMMEDIATELY_DESCRIPTION,
    SWAP_ON_DEATH_DESCRIPTION,
    SWAP_TYPE_BALANCE,
    SWAP_TYPES,
    TEAM_BALANCE_RATE_LIMIT_SEC,
    UNABLE_TO_SET_REDIS_KEY_ERROR_MSG,
)
from rcon.team_balance.models import DetailedPlayerInfo, RateLimitError, RCONTeamView

logger = logging.getLogger(__name__)


def get_team_player_count(team_view: RCONTeamView, team_name: str) -> int:
    """Return the number of players on the specified team."""
    player_count: int = 0

    team = team_view.get(team_name, None)
    # Relying on well formed team_views here, if we don't have one better to fail early on a key error
    if team:
        player_count = team_view[team_name]["count"]

    return player_count


def get_players_on_team(
    team_view: RCONTeamView, team_name: str
) -> List[DetailedPlayerInfo]:
    """Collect all the players on a specific team from the given team view."""
    team_players: List[DetailedPlayerInfo] = []

    team = team_view.get(team_name, None)

    # Relying on well formed team_views here, if we don't have one better to fail early on a key error
    if team:
        for squad in team["squads"].values():
            for player in squad["players"]:
                team_players.append(player)

        if team.get("commander", None):
            team_players.append(team["commander"])

    return team_players


def check_rate_limit(
    redis_store: redis.StrictRedis,
    rate_limit: int = TEAM_BALANCE_RATE_LIMIT_SEC,
    timestamp: Optional[datetime] = None,
) -> None:
    """Raise a RateLimitError if ran too recently or set the new run timestamp."""
    last_swap_timestamp = get_balance_timestamp(redis_store)
    if (
        last_swap_timestamp
        and (
            delta := (datetime.now(timezone.utc) - last_swap_timestamp)
        ).total_seconds()
        < rate_limit
    ):
        raise RateLimitError(
            BALANCE_RATE_LIMIT_EXCEEDED_ERROR_MSG.format(
                round(delta.total_seconds(), 1), rate_limit
            )
        )

    set_balance_timestamp(redis_store, timestamp)


def set_balance_timestamp(
    redis_store: redis.StrictRedis,
    timestamp: Optional[datetime] = None,
    redis_key: str = REDIS_BALANCE_KEY,
) -> None:
    """Set the UTC timestamp of the shuffle/balance attempt."""
    time_stamp = timestamp or datetime.now(timezone.utc)

    if not redis_store.set(redis_key, pickle.dumps(time_stamp)):
        raise redis.RedisError(UNABLE_TO_SET_REDIS_KEY_ERROR_MSG.format(redis_key))


def get_balance_timestamp(
    redis_store: redis.StrictRedis, redis_key: str = REDIS_BALANCE_KEY
) -> Optional[datetime]:
    """Return the UTC timestamp of the last shuffle/balance or None."""

    last_raw_timestamp = redis_store.get(redis_key)
    last_timestamp: Optional[datetime] = None
    if last_raw_timestamp:
        last_timestamp = pickle.loads(last_raw_timestamp)
        last_timestamp.replace(tzinfo=timezone.utc)

    return last_timestamp


# Force the steam_id_64 to be keyword only to prevent player name/steam ID confusion when calling
def set_player_swap_timestamp(
    redis_store: redis.StrictRedis,
    timestamp: Optional[datetime] = None,
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
    players: Sequence[DetailedPlayerInfo], num_to_select: int
) -> List[DetailedPlayerInfo]:
    """Select up to num_to_select players randomly from the given list of players"""
    if len(players) == 0:
        return []

    shuffled_players: List[DetailedPlayerInfo] = players[:]
    random.shuffle(shuffled_players)

    # If we don't have enough possible players to swap, use as many as possible
    if num_to_select > len(shuffled_players):
        return shuffled_players

    # Otherwise grab only the desired number of players
    return shuffled_players[0:num_to_select]


def get_player_session(player: DetailedPlayerInfo, most_recent: bool) -> datetime:
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
    players_to_swap: Iterable[DetailedPlayerInfo],
    swap_type: str,
    swap_on_death: bool = False,
    from_team: Optional[str] = None,
    to_team: Optional[str] = None,
) -> Tuple[List[DetailedPlayerInfo], List[DetailedPlayerInfo]]:
    """Swap players and handle logging."""

    swapped_axis_players: List[DetailedPlayerInfo] = []
    swapped_allied_players: List[DetailedPlayerInfo] = []

    switch_function: Callable[[str, None], None]
    switch_type: str
    if swap_on_death:
        switch_function = rcon_hook.do_switch_player_on_death
        switch_type = SWAP_ON_DEATH_DESCRIPTION
    else:
        switch_function = rcon_hook.do_switch_player_now
        switch_type = SWAP_IMMEDIATELY_DESCRIPTION

    for player in players_to_swap:
        # this function has a unused 'by' argument
        result = switch_function(player["name"], None)
        if result == "SUCCESS":
            set_player_swap_timestamp(
                redis_store,
                steam_id_64=player["steam_id_64"],
                swap_type=swap_type,
            )

            if player["team"] == ALLIED_TEAM:
                swapped_allied_players.append(player)
                destination_team = AXIS_TEAM
            elif player["team"] == AXIS_TEAM:
                swapped_axis_players.append(player)
                destination_team = ALLIED_TEAM

            if not from_team:
                from_team = player["team"]

            if not to_team:
                to_team = destination_team

            if swap_type == SWAP_TYPE_BALANCE:
                message = PLAYER_BALANCE_SWAP_MSG.format(
                    player["name"],
                    from_team,
                    player["steam_id_64"],
                    to_team,
                    switch_type,
                )
            else:
                message = PLAYER_SHUFFLE_SWAP_MSG.format(
                    player["name"],
                    from_team,
                    player["steam_id_64"],
                    to_team,
                )

            # When called with teamless players it's called one player a a time
            # When called for a list of players with more than one player we have to
            # reset these or these are stale values from the previous loop
            from_team = None
            to_team = None

            logger.info(message)
            audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)
        else:
            message = RCON_SWAP_FAILED_ERROR_MSG.format(
                player["name"], player["team"], player["steam_id_64"]
            )
            logger.error(message)
            audit(DISCORD_BALANCE_SHUFFLE_WEBHOOK, message)

        # time.sleep(RCON_TEAM_SWAP_DELAY_MS / 1000)

    return swapped_axis_players, swapped_allied_players


def swap_teamless_players(
    rcon_hook: RecordedRcon,
    redis_store: redis.StrictRedis,
    teamless_players_to_swap: Iterable[DetailedPlayerInfo],
    swap_type: str,
    swap_on_death: bool = False,
) -> None:
    """Handle swapping teamless players between teams evenly."""

    # Distribute teamless players to each team, choosing which team to start with at random
    # Whether or not to include teamless players is determined when collecting those players
    alternating_teams: Tuple[str, str] = (AXIS_TEAM, ALLIED_TEAM)
    if random.choice(alternating_teams) == ALLIED_TEAM:
        alternating_teams = (ALLIED_TEAM, AXIS_TEAM)

    for player, team in zip(teamless_players_to_swap, cycle(alternating_teams)):
        swap_players(
            rcon_hook,
            redis_store,
            [player],
            swap_type,
            swap_on_death,
            from_team=EMPTY_TEAM,
            to_team=ALLIED_TEAM,
        )
        # When swapping a teamless player, RCON defaults to putting them on the Allied team
        # and they have to be swapped twice to get to the Axis team
        if team == AXIS_TEAM:
            swap_players(
                rcon_hook,
                redis_store,
                [player],
                swap_type,
                swap_on_death,
                from_team=ALLIED_TEAM,
                to_team=AXIS_TEAM,
            )


def audit(
    discord_webhook_url: Optional[str], message: str, by="TeamAutoBalance"
) -> None:
    """Send message to the given Discord webhook."""
    webhook_url = None
    if discord_webhook_url is not None and discord_webhook_url != "":
        webhook_url = discord_webhook_url
        send_to_discord_audit(message, by=by, webhookurl=webhook_url, silent=False)
