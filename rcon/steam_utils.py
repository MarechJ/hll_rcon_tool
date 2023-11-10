import datetime
import logging
import math
import time
from typing import List, Mapping

import steam.exceptions
from steam.webapi import WebAPI

from rcon.cache_utils import ttl_cache
from rcon.config import get_config
from rcon.models import PlayerSteamID, SteamInfo
from rcon.types import SteamBanResultType, SteamBansType

logger = logging.getLogger(__name__)


def get_steam_api_key() -> str | None:
    steam_key = get_config().get("STEAM_API_KEY", None)
    if steam_key is None or steam_key == "":
        logger.warning("STEAM_API_KEY not set some features will be disabled.")

    return steam_key


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_steam_profile(steamd_id):
    profiles = get_steam_profiles([steamd_id])
    if not profiles or len(profiles) == 0:
        return None
    return profiles[0]


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_steam_profiles(steam_ids):
    steam_key = get_steam_api_key()

    if not steam_key:
        return None

    try:
        api = WebAPI(key=steam_key)
        return api.ISteamUser.GetPlayerSummaries(steamids=",".join(steam_ids))[
            "response"
        ]["players"]
    except steam.exceptions.SteamError as e:
        logger.error(e)
        return None
    except AttributeError:
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.error("Steam: no player found")
    except:
        logger.error("Unexpected error while fetching steam profile")
        return None


@ttl_cache(60 * 60 * 24 * 7, cache_falsy=True, is_method=False)
def get_player_country_code(steamd_id):
    profile = get_steam_profile(steamd_id)

    if not profile:
        return None

    is_private = profile.get("communityvisibilitystate", 1) != 3
    return profile.get("loccountrycode", "private" if is_private else "")


@ttl_cache(60 * 60, cache_falsy=True, is_method=False)
def get_players_country_code(steamd_ids: List[str]) -> Mapping:
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
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
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
def get_players_ban(steamd_ids: List):
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
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.error("Steam no player found")
        return None
    except:
        logger.error("Unexpected error while fetching steam bans")
        return None

    return bans


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
def get_players_have_bans(steamd_ids: List) -> Mapping[str, SteamBanResultType]:
    player_bans = get_players_ban(steamd_ids)

    result = dict.fromkeys(steamd_ids, {"steam_bans": None})
    if player_bans is None:
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
def get_player_has_bans(steamd_id):
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
            if not profiles:
                logger.error("Error while retrieving Steam profiles - Steam API may have returned a 'Too Many Requests' error")
                continue
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
