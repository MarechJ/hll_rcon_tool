import logging
import os
from functools import wraps
from rcon.commands import CommandFailedError

from discord_webhook import DiscordEmbed

from rcon.recorded_commands import RecordedRcon
from rcon.player_history import (
    save_player,
    save_start_player_session,
    save_end_player_session,
    safe_save_player_action,
    get_player,
    _get_set_player,
)
from rcon.game_logs import on_connected, on_disconnected, on_camera, on_chat
from rcon.models import enter_session, PlayerSteamID, SteamInfo, enter_session
from rcon.discord import send_to_discord_audit, dict_to_discord
from rcon.steam_utils import (
    get_player_bans,
    STEAM_KEY,
    get_steam_profile,
    get_hll_playtime_in_hours,
    update_db_player_info,
)
from rcon.discord import send_to_discord_audit
from rcon.user_config import CameraConfig
from rcon.discord import get_prepared_discord_hooks, send_to_discord_audit
from rcon.map_recorder import VoteMap
from rcon.user_config import VoteMapConfig
from rcon.workers import temporary_broadcast, temporary_welcome

logger = logging.getLogger(__name__)


@on_chat
def count_vote(rcon: RecordedRcon, struct_log):
    config = VoteMapConfig()
    if not config.get_vote_enabled():
        return

    v = VoteMap()
    if vote := v.is_vote(struct_log.get("sub_content")):
        logger.debug("Vote chat detected: %s", struct_log["message"])
        map_name = v.register_vote(
            struct_log["player"], struct_log["timestamp_ms"] / 1000, vote
        )
        try:
            temporary_broadcast(
                rcon,
                config.get_votemap_thank_you_text().format(
                    player_name=struct_log["player"], map_name=map_name
                ),
                5,
            )
        except Exception:
            logger.warning("Unable to output thank you message")
        v.apply_with_retry(nb_retry=2)


MAX_DAYS_SINCE_BAN = os.getenv("BAN_ON_VAC_HISTORY_DAYS", 0)
AUTO_BAN_REASON = os.getenv(
    "BAN_ON_VAC_HISTORY_REASON", "VAC ban history ({DAYS_SINCE_LAST_BAN} days ago)"
)
MAX_GAME_BAN_THRESHOLD = os.getenv("MAX_GAME_BAN_THRESHOLD", 0)
MIN_HLL_PLAYTIME_HOURS = int(os.getenv("MIN_HLL_PLAYTIME_HOURS", -1))

def ban_if_blacklisted(rcon: RecordedRcon, steam_id_64, name):
    with enter_session() as sess:
        player = get_player(sess, steam_id_64)

        if not player:
            logger.error("Can't check blacklist, player not found %s", steam_id_64)
            return

        if player.blacklist and player.blacklist.is_blacklisted:
            try:
                logger.info(
                    "Player %s was banned due blacklist, reason: %s",
                    str(name),
                    player.blacklist.reason,
                )
                rcon.do_perma_ban(
                    player=name,
                    reason=player.blacklist.reason,
                    by=f"BLACKLIST: {player.blacklist.by}",
                )
                safe_save_player_action(
                    rcon=rcon,
                    player_name=name,
                    action_type="PERMABAN",
                    reason=player.blacklist.reason,
                    by=f"BLACKLIST: {player.blacklist.by}",
                    steam_id_64=steam_id_64,
                )
                try:
                    send_to_discord_audit(
                        f"`BLACKLIST` -> {dict_to_discord(dict(player=name, reason=player.blacklist.reason))}",
                        "BLACKLIST",
                    )
                except:
                    logger.error("Unable to send blacklist to audit log")
            except:
                send_to_discord_audit(
                    "Failed to apply ban on blacklisted players, please check the logs and report the error",
                    "ERROR",
                )


def should_ban(bans, max_game_bans, max_days_since_ban):
    try:
        days_since_last_ban = int(bans["DaysSinceLastBan"])
        number_of_game_bans = int(bans.get("NumberOfGameBans", 0))
    except ValueError:  # In case DaysSinceLastBan can be null
        return

    has_a_ban = bans.get("VACBanned") == True or number_of_game_bans >= max_game_bans

    if days_since_last_ban <= 0:
        return False

    if days_since_last_ban <= max_days_since_ban and has_a_ban:
        return True

    return False


def ban_if_has_vac_bans(rcon: RecordedRcon, steam_id_64, name):
    try:
        max_days_since_ban = int(MAX_DAYS_SINCE_BAN)
        max_game_bans = (
            float("inf")
            if int(MAX_GAME_BAN_THRESHOLD) <= 0
            else int(MAX_GAME_BAN_THRESHOLD)
        )
    except ValueError:  # No proper value is given
        logger.error(
            "Invalid value given for environment variable BAN_ON_VAC_HISTORY_DAYS or MAX_GAME_BAN_THRESHOLD"
        )
        return

    if max_days_since_ban <= 0:
        return  # Feature is disabled

    with enter_session() as sess:
        player = get_player(sess, steam_id_64)

        if not player:
            logger.error("Can't check VAC history, player not found %s", steam_id_64)
            return

        bans = get_player_bans(steam_id_64)
        if not bans or not isinstance(bans, dict):
            logger.warning(
                "Can't fetch Bans for player %s, received %s", steam_id_64, bans
            )
            # Player couldn't be fetched properly (logged by get_player_bans)
            return

        if should_ban(bans, max_game_bans, max_days_since_ban):
            reason = AUTO_BAN_REASON.format(
                DAYS_SINCE_LAST_BAN=bans.get("DaysSinceLastBan"),
                MAX_DAYS_SINCE_BAN=str(max_days_since_ban),
            )
            logger.info(
                "Player %s was banned due VAC history, last ban: %s days ago",
                str(player),
                bans.get("DaysSinceLastBan"),
            )
            rcon.do_perma_ban(player=name, reason=reason, by="VAC BOT")

            try:
                audit_params = dict(
                    player=name,
                    steam_id_64=player.steam_id_64,
                    reason=reason,
                    days_since_last_ban=bans.get("DaysSinceLastBan"),
                    vac_banned=bans.get("VACBanned"),
                    number_of_game_bans=bans.get("NumberOfGameBans"),
                )
                send_to_discord_audit(
                    f"`VAC/GAME BAN` -> {dict_to_discord(audit_params)}", "AUTOBAN"
                )
            except:
                logger.exception("Unable to send vac ban to audit log")

def kick_if_low_playtime(rcon, struct_log, steam_id_64):    
    hll_timm_played = get_hll_playtime_in_hours(steam_id_64)
    if hll_timm_played is None or hll_timm_played < MIN_HLL_PLAYTIME_HOURS:
        logger.info(
            f"Kicking player %s for having less than {MIN_HLL_PLAYTIME_HOURS} hours played ({hll_timm_played})"
        )
        rcon.do_kick(player=struct_log["player"], reason=f"Playtime < {MIN_HLL_PLAYTIME_HOURS} hours or Steam Profile not public", by="VLL Admin")

def inject_steam_id_64(func):
    @wraps(func)
    def wrapper(rcon, struct_log):
        try:
            name = struct_log["player"]
            info = rcon.get_player_info(name)
            steam_id_64 = info.get("steam_id_64")
        except KeyError:
            logger.exception("Unable to inject steamid %s", struct_log)
            raise
        if not steam_id_64:
            logger.warning("Can't get player steam_id for %s", name)
            return

        return func(rcon, struct_log, steam_id_64)

    return wrapper


@on_connected
def handle_on_connect(rcon, struct_log):
    
    steam_id_64 = rcon.get_player_info.get_cached_value_for(struct_log["player"])

    try:
        if type(rcon) == RecordedRcon:
            rcon.invalidate_player_list_cache()
        else:
            rcon.get_player.cache_clear()
        rcon.get_player_info.clear_for(struct_log["player"])
        rcon.get_player_info.clear_for(player=struct_log["player"])
    except Exception:
        logger.exception("Unable to clear cache for %s", steam_id_64)
    try:
        info = rcon.get_player_info(struct_log["player"])
        steam_id_64 = info.get("steam_id_64")
    except (CommandFailedError, KeyError):
        if not steam_id_64:
            logger.exception("Unable to get player steam ID for %s", struct_log)
            raise
        else:
            logger.error(
                "Unable to get player steam ID for %s, falling back to cached value %s",
                struct_log,
                steam_id_64,
            )

    timestamp = int(struct_log["timestamp_ms"]) / 1000

    kick_if_low_playtime(rcon=rcon, struct_log=struct_log, steam_id_64=steam_id_64)

    save_player(
        struct_log["player"],
        steam_id_64,
        timestamp=int(struct_log["timestamp_ms"]) / 1000,
    )
    save_start_player_session(steam_id_64, timestamp=timestamp)
    ban_if_blacklisted(rcon, steam_id_64, struct_log["player"])
    ban_if_has_vac_bans(rcon, steam_id_64, struct_log["player"])

@on_disconnected
@inject_steam_id_64
def handle_on_disconnect(rcon, struct_log, steam_id_64):
    save_end_player_session(steam_id_64, struct_log["timestamp_ms"] / 1000)


@on_connected
@inject_steam_id_64
def update_player_steaminfo_on_connect(rcon, struct_log, steam_id_64):
    if not steam_id_64:
        logger.error(
            "Can't update steam info, no steam id available for %s",
            struct_log.get("player"),
        )
        return
    profile = get_steam_profile(steam_id_64)
    if not profile:
        logger.error(
            "Can't update steam info, no steam profile returned for %s",
            struct_log.get("player"),
        )
        return

    logger.info("Updating steam profile for player %s", struct_log["player"])
    with enter_session() as sess:
        player = _get_set_player(
            sess, player_name=struct_log["player"], steam_id_64=steam_id_64
        )
        update_db_player_info(player, profile)
        sess.commit()


@on_camera
def notify_camera(rcon: RecordedRcon, struct_log):
    send_to_discord_audit(message=struct_log["message"], by=struct_log["player"])

    try:
        if hooks := get_prepared_discord_hooks("camera"):
            embeded = DiscordEmbed(
                title=f'{struct_log["player"]}  - {struct_log["steam_id_64_1"]}',
                description=struct_log["sub_content"],
                color=242424,
            )
            for h in hooks:
                h.add_embed(embeded)
                h.execute()
    except Exception:
        logger.exception("Unable to forward to hooks")

    config = CameraConfig()
    if config.is_broadcast():
        temporary_broadcast(rcon, struct_log["message"], 60)

    if config.is_welcome():
        temporary_welcome(rcon, struct_log["message"], 60)
