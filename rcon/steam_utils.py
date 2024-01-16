import datetime
import logging
import math
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Iterable, Sequence

import steam.exceptions
from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
from steam.webapi import WebAPI

from rcon.cache_utils import ttl_cache
from rcon.models import PlayerSteamID, SteamInfo, enter_session
from rcon.types import SteamBansType, SteamInfoType, SteamPlayerSummaryType
from rcon.user_config.steam import SteamUserConfig
from rcon.utils import batched

logger = logging.getLogger(__name__)
last_steam_api_key_warning = datetime.datetime.now()

STEAM_API: WebAPI | None = None


def get_steam_api() -> WebAPI:
    """Maintain a single initialized instance of the Steam WebAPI"""
    global STEAM_API
    if STEAM_API is None:
        api_key = get_steam_api_key()
        STEAM_API = WebAPI(key=api_key)

    return STEAM_API


def get_steam_api_key() -> str | None:
    """Return the servers steam API key if configured"""
    global last_steam_api_key_warning

    config = SteamUserConfig.load_from_db()
    if config.api_key is None or config.api_key == "":
        timestamp = datetime.datetime.now()
        # Only log once every 5 minutes or it is super spammy
        if (timestamp - last_steam_api_key_warning).total_seconds() > 300:
            logger.warning("Steam API key is not set some features will be disabled.")
            last_steam_api_key_warning = timestamp

    return config.api_key


def is_steam_id_64(steam_id_64: str) -> bool:
    """Test if an ID is a steam_id_64 or a windows store ID"""
    if len(steam_id_64) == 17 and steam_id_64.isdigit():
        return True
    return False


def filter_steam_ids():
    """Remove any non steam ID player IDs from `steam_id_64s`"""

    def decorator(f):
        @wraps(f)
        def wrapper(steam_id_64s: Iterable[str], *args, **kwargs):
            # Remove any duplicates and sort to force redis cache hits even if the
            # originating call has steam IDs in different orders
            steam_id_64s = sorted(
                set([id_ for id_ in steam_id_64s if is_steam_id_64(id_)])
            )
            return f(steam_id_64s=steam_id_64s, *args, **kwargs)

        return wrapper

    return decorator


@dataclass
class ReturnValue:
    """Used to return a pickleable/callable object for the redis cache

    This avoids errors like:
        AttributeError: Can't pickle local object 'filter_steam_id.<locals>.decorator.<locals>.wrapper.<locals>.<lambda>'

    """

    def __init__(self, value: Any = None):
        self.value = value

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.value


def filter_steam_id(return_value: Any = None):
    """Return `return_value` if the wrapped function is called with a non steam ID"""

    def decorator(f):
        @wraps(f)
        def wrapper(steam_id_64: str, *args, **kwargs):
            if is_steam_id_64(steam_id_64):
                return f(steam_id_64=steam_id_64, *args, **kwargs)
            else:
                return ReturnValue(value=return_value)()

        return wrapper

    return decorator


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_id()
def fetch_steam_player_summary_player(
    steam_id_64: str,
) -> SteamPlayerSummaryType | None:
    """Fetch a single players steam profile

    This should never be used in any context where you know more than one steam ID
    in advance, instead use `fetch_steam_player_summary_mult_players` and pass all
    the steam IDs at once to reduce API calls
    """
    player_prof = fetch_steam_player_summary_mult_players(steam_id_64s=[steam_id_64])
    if player_prof:
        return player_prof.get(steam_id_64)


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_ids()
def fetch_steam_player_summary_mult_players(
    steam_id_64s: Iterable[str], page_size=100
) -> dict[str, SteamPlayerSummaryType]:
    """Fetch steam API profile info for each player

    https://partner.steamgames.com/doc/webapi/isteamuser

    This should be used in any context where we're querying more than a single
    player at a time because we can batch API calls for up to 100 steam IDs at a time
    """
    api = get_steam_api()

    # The steam API limits requests to 100 steam IDs at a time, process multiple
    # requests for any list larger than 100, but fit as many steam IDs into the
    # same API request as possible to help with rate limiting
    raw_profiles: list[SteamPlayerSummaryType] = []
    for chunk in batched(steam_id_64s, page_size):
        chunk_steam_ids = ",".join(chunk)
        try:
            logger.info("Fetching player summaries for %s steam IDs", len(chunk))
            raw_result = api.ISteamUser.GetPlayerSummaries(steamids=chunk_steam_ids)
            chunk_profiles: list[SteamPlayerSummaryType] = raw_result["response"][
                "players"
            ]
            raw_profiles.extend(chunk_profiles)
        except steam.exceptions.SteamError as e:
            logger.error(e)
        except AttributeError:
            logger.error("Steam API key is invalid, can't fetch steam profile")
            break
        except IndexError:
            logger.error("Steam: no player(s) found")
        except Exception as e:
            logger.exception(e)
            logger.error("Unexpected error while fetching steam profile")

    return {raw["steamid"]: raw for raw in raw_profiles}


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_ids()
def fetch_steam_bans_mult_players(
    steam_id_64s: Sequence[str], page_size=100
) -> dict[str, SteamBansType]:
    """Fetch steam API ban info for each player

    https://partner.steamgames.com/doc/webapi/isteamuser

    This should be used in any context where we're querying more than a single
    player at a time because we can batch API calls for up to 100 steam IDs at a time
    """
    api = get_steam_api()

    # The steam API limits requests to 100 steam IDs at a time, process multiple
    # requests for any list larger than 100, but fit as many steam IDs into the
    # same API request as possible to help with rate limiting
    raw_bans: list[SteamBansType] = []
    try:
        for chunk in batched(steam_id_64s, page_size):
            chunk_steam_ids = ",".join(chunk)
            logger.info("Fetching player bans for %s steam IDs", len(chunk))
            raw_result = api.ISteamUser.GetPlayerBans(  # type: ignore
                steamids=chunk_steam_ids
            )
            chunk_bans: SteamBansType = raw_result["players"]
            raw_bans.extend(chunk_bans)  # type: ignore

    except steam.exceptions.SteamError as e:
        logger.error(e)
    except AttributeError:
        logger.error("Steam API key is invalid, can't fetch steam profile")
    except IndexError:
        logger.error("Steam no player found")
    except:
        logger.error("Unexpected error while fetching steam bans")

    return {raw["SteamId"]: raw for raw in raw_bans}


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_id()
def fetch_steam_bans_player(steam_id_64: str) -> SteamBansType | None:
    """Fetch a single players steam bans

    This should never be used in any context where you know more than one steam ID
    in advance, instead use `fetch_steam_bans_mult_players` and pass all
    the steam IDs at once to reduce API calls
    """
    player = fetch_steam_bans_mult_players(steam_id_64s=[steam_id_64])
    if player:
        return player.get(steam_id_64)


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
def get_steam_profiles_mult_players(
    steam_id_64s: Iterable[str], sess: Session | None = None
) -> dict[str, SteamInfoType | None]:
    """Query the database for the specified players steam info (profile/country/bans)"""
    stmt = (
        select(PlayerSteamID)
        .options(joinedload(PlayerSteamID.steaminfo))
        .where(PlayerSteamID.steam_id_64.in_(steam_id_64s))
    )

    profiles: dict[str, SteamInfoType | None] = dict.fromkeys(steam_id_64s, None)
    if sess is None:
        with enter_session() as sess:
            # Needed to avoid an DetachedInstanceError error
            sess.expire_on_commit = False
            players = sess.scalars(stmt).all()
    else:
        players = sess.scalars(stmt).all()

    for p in players:
        profiles[p.steam_id_64] = p.steaminfo.to_dict() if p.steaminfo else None

    return profiles


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
def get_steam_profile(
    steam_id_64: str, sess: Session | None = None
) -> SteamInfoType | None:
    """Query the database for a specific players steam info (profile/country/bans)"""
    return get_steam_profiles_mult_players(steam_id_64s=[steam_id_64], sess=sess).get(
        steam_id_64
    )


def _get_player_country_code(profile: SteamPlayerSummaryType | None):
    """Extract a players 2 digit ISO 3166 country code from their steam profile"""
    if not profile:
        return None

    is_private = profile.get("communityvisibilitystate", 1) != 3
    return profile.get("loccountrycode", "private" if is_private else None)


def update_db_player_info(
    sess: Session, players: list[PlayerSteamID]
) -> tuple[int, int]:
    """Fetch steam API info for each player and update their database record

    This should be used in any context where we're updating more than a single
    player at a time because we can batch API calls for up to 100 steam IDs at a time

    Args:
        sess: An sqlalchemy session, unused but included to force it to only be
            called from within an active session so the database records will be updated
        player: A list of player records
    """
    steam_id_64s = [player.steam_id_64 for player in players]
    profiles = fetch_steam_player_summary_mult_players(steam_id_64s=steam_id_64s)
    bans = fetch_steam_bans_mult_players(steam_id_64s=steam_id_64s)

    for player in players:
        player_prof = profiles.get(player.steam_id_64)
        player_ban = bans.get(player.steam_id_64)

        # Don't edit the record and change the updated time if we have no new information
        if player_prof is None and player_ban is None:
            continue

        country_code = _get_player_country_code(player_prof)
        if player.steaminfo:
            player.steaminfo.profile = player_prof
            player.steaminfo.bans = player_ban
            player.steaminfo.country = country_code
        else:
            player.steaminfo = SteamInfo(
                profile=player_prof, bans=player_ban, country=country_code
            )

    return len(profiles), len(bans)


def update_missing_old_steam_info_single_player(
    sess: Session,
    player: PlayerSteamID,
    age_limit: datetime.timedelta = datetime.timedelta(hours=12),
):
    """Fetch steam API info if missing or older than age_limit for a single player

    Since this only calls the API for a single steam ID at a time and the requests
    can include up to 100 steam IDs, this should only be used in the context where we're
    updating info for a single player at a time, like when they connect to the game server

    Args:
        sess: An sqlalchemy session, unused but included to force it to only be
            called from within an active session so the database records will be updated
        player: The desired players database record
        age_limit: timedelta after which a refresh will be attempted from the steam API
    """

    if (
        player.steaminfo is None
        or player.steaminfo
        and player.steaminfo.updated
        and (datetime.datetime.utcnow() - player.steaminfo.updated) >= age_limit
    ):
        # Fetch both the profile and bans
        profile = fetch_steam_player_summary_player(player.steam_id_64)
        country_code = _get_player_country_code(profile)
        bans = fetch_steam_bans_player(player.steam_id_64)
        steam_info = SteamInfo(
            profile=profile,
            country=country_code,
            bans=bans,
        )
        player.steaminfo = steam_info
    elif player.steaminfo and player.steaminfo.bans is None:
        # Fetch the bans
        bans = fetch_steam_bans_player(player.steam_id_64)
        player.steaminfo.bans = bans
    elif (
        player.steaminfo
        and player.steaminfo.profile is None
        or player.steaminfo.country is None
    ):
        # Fetch the profile
        profile = fetch_steam_player_summary_player(player.steam_id_64)
        country_code = _get_player_country_code(profile)
        player.steaminfo.profile = profile
        player.steaminfo.country = country_code


def enrich_db_users(chunk_size=100, update_from_days_old=30):
    """Use the Steam API to update steam profiles/bans for missing or old records"""
    max_age = datetime.datetime.utcnow() - datetime.timedelta(days=update_from_days_old)
    with enter_session() as sess:
        # Missing JSONB records are surprisingly difficult to identify depending
        # on how they've been persisted but JSONB.NULL should cover the different cases
        # This query can also return many thousands of results, using stream_results and
        # yield_per doesn't fetch all of the results at once, but pages through them
        stmt = (
            select(PlayerSteamID)
            .execution_options(stream_results=True, yield_per=chunk_size)
            .outerjoin(SteamInfo)
            .where(func.length(PlayerSteamID.steam_id_64) == 17)
            .where(
                or_(
                    PlayerSteamID.steaminfo == None,
                    SteamInfo.updated <= max_age,
                    SteamInfo.bans == JSONB.NULL,
                    SteamInfo.profile == JSONB.NULL,
                )
            )
        )

        logger.info("Updating steam profiles/bans for missing/old users")
        for idx, player_chunks in enumerate(sess.scalars(stmt).partitions()):
            players = list(player_chunks)
            if not players:
                logger.warning("Empty query results for page %s", idx)
                continue
            logger.info(
                "Updating page %s steam profile/bans, first steam ID of page: %s",
                idx + 1,
                players[0],
            )
            num_profs, num_bans = update_db_player_info(sess, players=players)

            logger.info(
                "%s profiles, %s bans fetched from steam API",
                num_profs,
                num_bans,
            )

            # Shouldn't really need this with how many API calls we should be able to make
            # but just to be on the safe side
            time.sleep(1)


if __name__ == "__main__":
    enrich_db_users()
