import os
import logging
import datetime
import math
import time

from steam.webapi import WebAPI
from rcon.models import PlayerSteamID, SteamInfo
from rcon.cache_utils import ttl_cache

logger = logging.getLogger(__name__)

HLL_STEAM_APP_ID = 686810
STEAM_KEY = os.getenv('STEAM_API_KEY')
if not STEAM_KEY:
    logger.warning("STEAM_API_KEY not set some features will be disabled.")


@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_steam_profile(steamd_id):
    profiles = get_steam_profiles([steamd_id])

    if not profiles or len(profiles) == 0:
        return None
    
    time_played = get_hll_playtime_in_hours(steam_id=steamd_id)
    profiles[0]['hll_game_playtime'] = time_played
    return profiles[0]



@ttl_cache(60 * 60 * 24, cache_falsy=False, is_method=False)
def get_steam_profiles(steam_ids):
    if not STEAM_KEY:
        return None
    try:
        api = WebAPI(key=STEAM_KEY)
        return api.ISteamUser.GetPlayerSummaries(steamids=','.join(steam_ids))["response"]["players"]
    except AttributeError:
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
    except IndexError:
        logger.exception("Steam: no player found")
    except:
        logging.exception('Unexpected error while fetching steam profile')
        return None

@ttl_cache(60 * 5, cache_falsy=False, is_method=False)
def get_hll_playtime_in_hours(steam_id):
    if not STEAM_KEY:
        return None
    try:
        api = WebAPI(key=STEAM_KEY)
        # https://developer.valvesoftware.com/wiki/Steam_Web_API#GetOwnedGames_.28v0001.29

        
        response = api.IPlayerService.GetOwnedGames_v1(
            steamid=steam_id, 
            include_appinfo=True, 
            include_played_free_games=False, 
            appids_filter=[HLL_STEAM_APP_ID], # hardcode HLL steam appid
            include_free_sub=False)['response']

        print ("api_repos", HLL_STEAM_APP_ID, steam_id)
        print ("respo", response)
        if not response or len(response) == 0:
            return None
        
        # get playtime in minutes
        hll_game_playtime = response['games'][0]['playtime_forever']
        # return playtime in hours
        return round(hll_game_playtime*1.0/60)

    except AttributeError:
        logger.error("STEAM_API_KEY is invalid, can't fetch steam profile")
        return None
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


def update_db_player_info(player: PlayerSteamID, steam_profile):
    if not player.steaminfo:
        player.steaminfo = SteamInfo()
    player.steaminfo.profile = steam_profile
    player.steaminfo.country = steam_profile.get('loccountrycode')


def enrich_db_users(chunk_size=100, update_from_days_old=30):
    from rcon.models import enter_session, SteamInfo, PlayerSteamID
    from sqlalchemy import or_

    max_age = datetime.datetime.utcnow() - datetime.timedelta(days=update_from_days_old)
    with enter_session() as sess:
        query = sess.query(
            PlayerSteamID
        ).outerjoin(
            SteamInfo
        ).filter(
            or_(PlayerSteamID.steaminfo == None, SteamInfo.updated <= max_age)
        )
        
        pages = math.ceil(query.count() / chunk_size)
        for page in range(pages):
            by_ids = {p.steam_id_64: p for p in query.limit(chunk_size).all()}
            profiles = get_steam_profiles(list(by_ids.keys()))
            logger.info("Updating steam profiles page %s of %s - result count (query) %s - result count (steam) %s", 
                        page + 1, pages, len(by_ids), len(profiles))
            if not by_ids:
                logger.warning("Empty query results")
                continue
            for p in profiles:
                player = by_ids.get(p['steamid'])
                if not player:
                    logger.warning("Unable to find player %s", p["steamid"])
                    continue
                #logger.debug("Saving info for %s: %s", player.steam_id_64, p)
                update_db_player_info(player=player, steam_profile=p)

            sess.commit()
            time.sleep(5)
           

            

if __name__ == "__main__":
    enrich_db_users()