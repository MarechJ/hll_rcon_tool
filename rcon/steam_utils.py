import datetime
import logging
import math
import time
from functools import wraps
from typing import Any, Mapping

import steam.exceptions
from steam.webapi import WebAPI
from dataclasses import dataclass

from rcon.cache_utils import ttl_cache
from rcon.models import PlayerSteamID, SteamInfo
from rcon.types import SteamBanResultType, SteamBansType
from rcon.user_config.steam import SteamUserConfig

logger = logging.getLogger(__name__)

last_steam_api_key_warning = datetime.datetime.now()


def is_steam_id_64(steam_id_64: str) -> bool:
    if len(steam_id_64) == 17 and steam_id_64.isdigit():
        return True
    return False


def filter_steam_ids():
    def decorator(f):
        @wraps(f)
        def wrapper(steamd_ids: list[str], *args, **kwargs):
            steamd_ids = [id_ for id_ in steamd_ids if is_steam_id_64(id_)]
            return f(*args, steamd_ids=steamd_ids, **kwargs)

        return wrapper

    return decorator


@dataclass
class ReturnValue:
    """Used to return a cacheable/callable object for the redis cache

    This avoids errors like:
        AttributeError: Can't pickle local object 'filter_steam_id.<locals>.decorator.<locals>.wrapper.<locals>.<lambda>'

    """

    def __init__(self, value: Any = None):
        self.value = value

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.value


def filter_steam_id(return_value: Any = None):
    def decorator(f):
        @wraps(f)
        def wrapper(steamd_id: str, *args, **kwargs):
            if is_steam_id_64(steamd_id):
                return f(steamd_id=steamd_id, *args, **kwargs)
            else:
                return ReturnValue(value=return_value)()

        return wrapper

    return decorator


def get_steam_api_key() -> str | None:
    global last_steam_api_key_warning

    config = SteamUserConfig.load_from_db()
    if config.api_key is None or config.api_key == "":
        timestamp = datetime.datetime.now()
        # Only log once every 5 minutes or it is super spammy
        if (timestamp - last_steam_api_key_warning).total_seconds() > 300:
            logger.warning("Steam API key is not set some features will be disabled.")
            last_steam_api_key_warning = timestamp

    return config.api_key


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
@filter_steam_id()
def get_steam_profile(steamd_id) -> Any | None:
    profiles = get_steam_profiles([steamd_id])
    if not profiles or len(profiles) == 0:
        return None
    return profiles[0]


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
@filter_steam_ids()
def get_steam_profiles(steamd_ids: list[str]):
    steam_key = get_steam_api_key()

    if not steam_key:
        return None

    try:
        api = WebAPI(key=steam_key)
        return api.ISteamUser.GetPlayerSummaries(steamids=",".join(steamd_ids))[
            "response"
        ]["players"]
    except steam.exceptions.SteamError as e:
        logger.error(e)
        return None
    except AttributeError:
        logger.error("Steam API key is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.error("Steam: no player found")
    except:
        logger.error("Unexpected error while fetching steam profile")
        return None


@ttl_cache(60 * 60 * 24 * 7, cache_falsy=True, is_method=False)
@filter_steam_id()
def get_player_country_code(steamd_id) -> Any | None:
    profile = get_steam_profile(steamd_id)

    if not profile:
        return None

    is_private = profile.get("communityvisibilitystate", 1) != 3
    return profile.get("loccountrycode", "private" if is_private else "")


@ttl_cache(60 * 60, cache_falsy=True, is_method=False)
@filter_steam_ids()
def get_players_country_code(steamd_ids: list[str]) -> Mapping:
    profiles = get_steam_profiles(steamd_ids)

    result = dict.fromkeys(steamd_ids, {"country": None})
    if not profiles:
        return result

    for profile in profiles:
        is_private = profile.get("communityvisibilitystate", 1) != 3
        country = profile.get("loccountrycode", "private" if is_private else "")
        result[profile["steamid"]] = {"country": country}

    return result


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_id()
def get_player_bans(steamd_id) -> SteamBansType | None:
    steam_key = get_steam_api_key()

    if not steam_key:
        return None

    try:
        api = WebAPI(key=steam_key)
        bans = api.ISteamUser.GetPlayerBans(steamids=steamd_id)["players"][0]
    except steam.exceptions.SteamError as e:
        logger.error(e)
        return None
    except AttributeError:
        logger.error("Steam API key is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.error("Steam no player found")
        return None
    except:
        logger.error("Unexpected error while fetching steam bans")
        return None

    if not bans:
        bans = {}
    return bans


@ttl_cache(60 * 60, cache_falsy=False, is_method=False)
@filter_steam_ids()
def get_players_ban(steamd_ids: list[str]):
    steam_key = get_steam_api_key()

    if not steam_key:
        return None

    try:
        api = WebAPI(key=steam_key)
        bans = api.ISteamUser.GetPlayerBans(steamids=",".join(steamd_ids))["players"]
    except steam.exceptions.SteamError as e:
        logger.error(e)
        return None
    except AttributeError:
        logger.error("Steam API key is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.error("Steam no player found")
        return None
    except:
        logger.error("Unexpected error while fetching steam bans")
        return None

    return bans


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_ids()
def get_players_have_bans(steamd_ids: list[str]) -> Mapping[str, SteamBanResultType]:
    player_bans = get_players_ban(steamd_ids)

    result = dict.fromkeys(steamd_ids, {"steam_bans": None})
    if player_bans is None:
        if steamd_ids:
            logger.warning("Unable to read bans for %s" % steamd_ids)
        return result

    for bans in player_bans:
        bans["has_bans"] = any(
            bans.get(k)
            for k in [
                "VACBanned",
                "NumberOfVACBans",
                "DaysSinceLastBan",
                "NumberOfGameBans",
            ]
        )
        result[bans["SteamId"]] = {"steam_bans": bans}
        del bans["SteamId"]

    return result


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
@filter_steam_id(return_value=dict())
def get_player_has_bans(steamd_id: str):
    bans = get_player_bans(steamd_id)

    if bans is None:
        logger.warning("Unable to read bans for %s" % steamd_id)
        bans = {}

    bans["has_bans"] = any(
        bans.get(k)
        for k in [
            "VACBanned",
            "NumberOfVACBans",
            "DaysSinceLastBan",
            "NumberOfGameBans",
        ]
    )
    return bans


def update_db_player_info(player: PlayerSteamID, steam_profile):
    if not player.steaminfo:
        player.steaminfo = SteamInfo()
    player.steaminfo.profile = steam_profile
    player.steaminfo.country = steam_profile.get("loccountrycode")


def enrich_db_users(chunk_size=100, update_from_days_old=30):
    from sqlalchemy import or_

    from rcon.models import PlayerSteamID, SteamInfo, enter_session

    max_age = datetime.datetime.utcnow() - datetime.timedelta(days=update_from_days_old)
    with enter_session() as sess:
        query = (
            sess.query(PlayerSteamID)
            .outerjoin(SteamInfo)
            .filter(or_(PlayerSteamID.steaminfo == None, SteamInfo.updated <= max_age))
        )

        pages = math.ceil(query.count() / chunk_size)
        for page in range(pages):
            by_ids = {p.steam_id_64: p for p in query.limit(chunk_size).all()}
            if not by_ids:
                logger.warning("Empty query results")
                continue
            profiles = get_steam_profiles(list(by_ids.keys()))
            if profiles is None:
                profiles = []
            logger.info(
                "Updating steam profiles page %s of %s - result count (query) %s - result count (steam) %s",
                page + 1,
                pages,
                len(by_ids),
                len(profiles),
            )
            for p in profiles:
                player = by_ids.get(p["steamid"])
                if not player:
                    logger.warning("Unable to find player %s", p["steamid"])
                    continue
                # logger.debug("Saving info for %s: %s", player.steam_id_64, p)
                update_db_player_info(player=player, steam_profile=p)

            sess.commit()
            time.sleep(5)


if __name__ == "__main__":
    enrich_db_users()
