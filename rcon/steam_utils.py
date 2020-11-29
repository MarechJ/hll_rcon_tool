import os
import logging

from steam.webapi import WebAPI

from rcon.cache_utils import ttl_cache

logger = logging.getLogger(__name__)

STEAM_KEY = os.getenv('STEAM_API_KEY')
if not STEAM_KEY:
    logger.warning("STEAM_API_KEY not set some features will be disabled. %s", os.environ)


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_steam_profile(steamd_id):
    if not STEAM_KEY:
        return None
    try:
        api = WebAPI(key=STEAM_KEY)
        return api.ISteamUser.GetPlayerSummaries(steamids=steamd_id)["response"]["players"][0]
    except AttributeError:
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.exception("Steam: no player found")
    except:
        logging.exception('Unexpected error while fetching steam profile')
        return None


def get_player_country_code(steamd_id):
    profile = get_steam_profile(steamd_id)
 
    if not profile:
        return None

    is_private = profile.get('communityvisibilitystate', 1) != 3
    return profile.get('loccountrycode', 'private' if is_private else '')


@ttl_cache(60 * 60 * 12, cache_falsy=False, is_method=False)
def get_player_bans(steamd_id):
    if not STEAM_KEY:
        return None

    try:
        api = WebAPI(key=STEAM_KEY)
        bans = api.ISteamUser.GetPlayerBans(steamids=steamd_id)['players'][0]
    except AttributeError:
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
    except IndexError:     
        logger.exception("Steam no player found")
        return None
    except:
        logging.exception('Unexpected error while fetching steam profile')
        return None

    if not bans:
        bans = {}
    return bans

@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_player_has_bans(steamd_id):
    bans = get_player_bans(steamd_id)

    if bans is None:
        logger.warning("Unable to read bans for %s" % steamd_id)
        bans = {}
        
    bans['has_bans'] = any(bans.get(k) for k in ['VACBanned', 'NumberOfVACBans', 'DaysSinceLastBan', 'NumberOfGameBans']) 
    return bans


if __name__ == "__main__":
    print(get_player_bans('76561198436700508'))