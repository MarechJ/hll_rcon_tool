import logging
import os
import re
from collections import defaultdict
from datetime import datetime
from functools import partial, wraps
from threading import Timer
from typing import DefaultDict, Dict, List, Optional, Sequence, Union

from discord_webhook import DiscordEmbed

import discord
from rcon.cache_utils import invalidates
from rcon.commands import CommandFailedError, HLLServerError
from rcon.config import get_config
from rcon.discord import (
    dict_to_discord,
    get_prepared_discord_hooks,
    send_to_discord_audit,
)
from rcon.discord_chat import make_hook
from rcon.game_logs import (
    on_camera,
    on_chat,
    on_connected,
    on_disconnected,
    on_generic,
    on_match_end,
    on_match_start,
)
from rcon.models import LogLineWebHookField, enter_session
from rcon.player_history import (
    _get_set_player,
    get_player,
    safe_save_player_action,
    save_end_player_session,
    save_player,
    save_start_player_session,
)
from rcon.rcon import Rcon, StructuredLogLineType
from rcon.steam_utils import get_player_bans, get_steam_profile, update_db_player_info
from rcon.types import PlayerFlagType, SteamBansType, VACGameBansConfigType
from rcon.user_config import CameraConfig, RealVipConfig
from rcon.utils import LOG_MAP_NAMES_TO_MAP, MapsHistory, get_server_number, UNKNOWN_MAP_NAME
from rcon.vote_map import VoteMap
from rcon.workers import record_stats_worker, temporary_broadcast, temporary_welcome

logger = logging.getLogger(__name__)


@on_chat
def count_vote(rcon: Rcon, struct_log: StructuredLogLineType):
    enabled = VoteMap().handle_vote_command(rcon=rcon, struct_log=struct_log)
    if enabled and (match := re.match(r"\d\s*$", struct_log["sub_content"].strip())):
        rcon.do_message_player(
            steam_id_64=struct_log["steam_id_64_1"],
            message=f"INVALID VOTE\n\nUse: !votemap {match.group()}",
        )

@on_chat
def send_info(rcon: Rcon, struct_log: StructuredLogLineType):
    message = struct_log.get("sub_content", "").strip()
    trigger_words = get_config()["TRIGGER_WORDS"]
    for word, output in trigger_words.items():
        if message.startswith(word):
            rcon.do_message_player(
                steam_id_64=struct_log["steam_id_64_1"], message=output
            )


def initialise_vote_map(rcon: Rcon, struct_log):
    logger.info("New match started initializing vote map. %s", struct_log)
    try:
        vote_map = VoteMap()
        vote_map.clear_votes()
        vote_map.gen_selection()
        vote_map.reset_last_reminder_time()
        vote_map.apply_results()
    except:
        logger.exception("Something went wrong in vote map init")


@on_match_end
def remind_vote_map(rcon: Rcon, struct_log):
    logger.info("Match ended reminding to vote map. %s", struct_log)
    vote_map = VoteMap()
    vote_map.apply_with_retry()
    vote_map.vote_map_reminder(rcon, force=True)


@on_match_start
def handle_new_match_start(rcon: Rcon, struct_log):
    try:
        logger.info("New match started recording map %s", struct_log)
        with invalidates(Rcon.get_map):
            try:
                current_map = rcon.get_map().replace("_RESTART", "")
            except (CommandFailedError, HLLServerError):
                current_map = "bla_"
                logger.error("Unable to get current map")

        map_name_to_save = LOG_MAP_NAMES_TO_MAP.get(
            struct_log["sub_content"], UNKNOWN_MAP_NAME
        )
        guessed = True
        log_map_name = struct_log["sub_content"].rsplit(" ")[0]
        log_time = datetime.fromtimestamp(struct_log["timestamp_ms"] / 1000)
        # Check that the log is less than 5min old
        if (datetime.utcnow() - log_time).total_seconds() < 5 * 60:
            # then we use the current map to be more accurate
            if (
                current_map.split("_")[0].lower()
                == map_name_to_save.split("_")[0].lower()
            ):
                map_name_to_save = current_map
                guessed = False
            elif map_name_to_save == UNKNOWN_MAP_NAME:
                map_name_to_save = current_map
                guessed = True
            else:
                logger.warning(
                    "Got recent match start but map don't match %s != %s",
                    map_name_to_save,
                    current_map,
                )

        # TODO added guess - check if it's already in there - set prev end if None
        maps_history = MapsHistory()

        if len(maps_history) > 0:
            if maps_history[0]["end"] is None and maps_history[0]["name"]:
                maps_history.save_map_end(
                    old_map=maps_history[0]["name"],
                    end_timestamp=int(struct_log["timestamp_ms"] / 1000) - 100,
                )

        maps_history.save_new_map(
            new_map=map_name_to_save,
            guessed=guessed,
            start_timestamp=int(struct_log["timestamp_ms"] / 1000),
        )
    except:
        raise
    finally:
        initialise_vote_map(rcon, struct_log)
        try:
            record_stats_worker(MapsHistory()[1])
        except Exception:
            logger.exception("Unexpected error while running stats worker")


@on_match_end
def record_map_end(rcon: Rcon, struct_log):
    logger.info("Match ended recording map %s", struct_log)
    maps_history = MapsHistory()
    try:
        current_map = rcon.get_map()
    except (CommandFailedError, HLLServerError):
        current_map = "bla_"
        logger.error("Unable to get current map")

    map_name = LOG_MAP_NAMES_TO_MAP.get(struct_log["sub_content"], UNKNOWN_MAP_NAME)
    log_time = datetime.fromtimestamp(struct_log["timestamp_ms"] / 1000)

    if (datetime.utcnow() - log_time).total_seconds() < 60:
        # then we use the current map to be more accurate
        if current_map.split("_")[0].lower() == map_name.split("_")[0].lower():
            maps_history.save_map_end(
                current_map, end_timestamp=int(struct_log["timestamp_ms"] / 1000)
            )


def ban_if_blacklisted(rcon: Rcon, steam_id_64, name):
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


def should_ban(
    bans: SteamBansType | None,
    max_game_bans: float,
    max_days_since_ban: int,
    player_flags: list[PlayerFlagType] = [],
    whitelist_flags: list[str] = [],
) -> bool | None:
    if not bans:
        return

    if any(player_flag in whitelist_flags for player_flag in player_flags):
        return False

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


def ban_if_has_vac_bans(rcon: Rcon, steam_id_64, name):
    try:
        config: VACGameBansConfigType = get_config()["VAC_GAME_BANS"]
    except KeyError:
        logger.error(f"VAC_GAME_BANS not in your config")
        return

    max_days_since_ban = config.get("ban_on_vac_history_days", 0)
    max_game_bans = (
        float("inf")
        if config.get("max_game_ban_threshold", 0) <= 0
        else config.get("max_game_ban_threshold", 0)
    )
    whitelist_flags = config.get("whitelist_flags", [])

    if max_days_since_ban <= 0:
        return  # Feature is disabled

    with enter_session() as sess:
        player = get_player(sess, steam_id_64)

        if not player:
            logger.error("Can't check VAC history, player not found %s", steam_id_64)
            return

        bans: SteamBansType | None = get_player_bans(steam_id_64)
        if not bans or not isinstance(bans, dict):
            logger.warning(
                "Can't fetch Bans for player %s, received %s", steam_id_64, bans
            )
            # Player couldn't be fetched properly (logged by get_player_bans)
            return

        if should_ban(
            bans,
            max_game_bans,
            max_days_since_ban,
            player_flags=player.flags,
            whitelist_flags=whitelist_flags,
        ):
            reason = config["ban_on_vac_history_reason"].format(
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


def inject_player_ids(func):
    @wraps(func)
    def wrapper(rcon, struct_log: StructuredLogLineType):
        name = struct_log["player"]
        steam_id_64 = struct_log["steam_id_64_1"]
        return func(rcon, struct_log, name, steam_id_64)

    return wrapper


@on_connected
@inject_player_ids
def handle_on_connect(rcon: Rcon, struct_log, name, steam_id_64):
    try:
        rcon.get_players.cache_clear()
        rcon.get_player_info.clear_for(struct_log["player"])
        rcon.get_player_info.clear_for(player=struct_log["player"])
    except Exception:
        logger.exception("Unable to clear cache for %s", steam_id_64)

    timestamp = int(struct_log["timestamp_ms"]) / 1000
    if not steam_id_64:
        logger.error(
            "Unable to get player steam ID for %s, can't process connection",
            struct_log,
        )
        return
    save_player(
        struct_log["player"],
        steam_id_64,
        timestamp=int(struct_log["timestamp_ms"]) / 1000,
    )
    save_start_player_session(steam_id_64, timestamp=timestamp)
    ban_if_blacklisted(rcon, steam_id_64, struct_log["player"])
    ban_if_has_vac_bans(rcon, steam_id_64, struct_log["player"])


@on_disconnected
@inject_player_ids
def handle_on_disconnect(rcon, struct_log, _, steam_id_64):
    save_end_player_session(steam_id_64, struct_log["timestamp_ms"] / 1000)


@on_connected
@inject_player_ids
def update_player_steaminfo_on_connect(rcon, struct_log, _, steam_id_64):
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


pendingTimers = {}


@on_connected
@inject_player_ids
def notify_false_positives(rcon: Rcon, _, name: str, steam_id_64: str):
    c = get_config()["NOLEADER_AUTO_MOD"]
    if not c["enabled"]:
        logger.info("no leader auto mod is disabled")
        return

    if not name.endswith(" "):
        return

    logger.info(
        "Detected player name with whitespace at the end: Warning them of false-positive events. Player name: "
        + name
    )

    try:
        send_to_discord_audit(
            f"WARNING Player with bugged profile joined: `{name}` `{steam_id_64}`\n\nThis player if Squad Officer will cause their squad to be punished. They also will show as unassigned in the Game view.\n\nPlease ask them to change their name (last character IG shouldn't be a whitespace)"
        )
    except Exception:
        logger.exception("Unable to send to audit")

    def notify_player():
        try:
            rcon.do_message_player(
                steam_id_64=steam_id_64,
                message=c["whitespace_names_message"],
                by="CRcon",
                save_message=False,
            )
        except Exception as e:
            logger.error("Could not message player " + name + "/" + steam_id_64, e)

    # The player might not yet have finished connecting in order to send messages.
    t = Timer(10, notify_player)
    pendingTimers[steam_id_64] = t
    t.start()


@on_disconnected
@inject_player_ids
def cleanup_pending_timers(_, _1, _2, steam_id_64: str):
    pt: Timer = pendingTimers.pop(steam_id_64, None)
    if pt is None:
        return
    if pt.is_alive():
        try:
            pt.cancel()
        except:
            pass


def _set_real_vips(rcon: Rcon, struct_log):
    config = RealVipConfig()
    if not config.get_enabled():
        logger.debug("Real VIP is disabled")
        return

    desired_nb_vips = config.get_desired_total_number_vips()
    min_vip_slot = config.get_minimum_number_vip_slot()
    vip_count = rcon.get_vips_count()

    remaining_vip_slots = max(desired_nb_vips - vip_count, max(min_vip_slot, 0))
    rcon.set_vip_slots_num(remaining_vip_slots)
    logger.info("Real VIP set slots to %s", remaining_vip_slots)


@on_connected
def do_real_vips(rcon: Rcon, struct_log):
    _set_real_vips(rcon, struct_log)


@on_disconnected
def undo_real_vips(rcon: Rcon, struct_log):
    _set_real_vips(rcon, struct_log)


@on_camera
def notify_camera(rcon: Rcon, struct_log):
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


def make_allowed_mentions(mentions: Sequence[str]) -> discord.AllowedMentions:
    """Convert the provided sequence of users and roles to a discord.AllowedMentions

    Similar to discord_chat.make_allowed_mentions but doesn't strip @everyone/@here
    """
    allowed_mentions: DefaultDict[str, List[discord.Object]] = defaultdict(list)

    for role_or_user in mentions:
        if match := re.match(r"<@(\d+)>", role_or_user):
            allowed_mentions["users"].append(discord.Object(int(match.group(1))))
        if match := re.match(r"<@&(\d+)>", role_or_user):
            allowed_mentions["roles"].append(discord.Object(int(match.group(1))))

    return discord.AllowedMentions(
        users=allowed_mentions["users"], roles=allowed_mentions["roles"]
    )


def send_log_line_webhook_message(
    webhook_url: str,
    mentions: Optional[Sequence[str]],
    _,
    log_line: Dict[str, Union[str, int, float, None]],
) -> None:
    """Send a time stammped embed of the log_line and mentions to the provided Discord Webhook"""

    mentions = mentions or []

    webhook = make_hook(webhook_url)
    allowed_mentions = make_allowed_mentions(mentions)

    SERVER_SHORT_NAME = os.getenv("SERVER_SHORT_NAME", "No Server Name Set")

    content = " ".join(mentions)
    description = log_line["line_without_time"]
    embed = discord.Embed(
        description=description,
        timestamp=datetime.utcfromtimestamp(log_line["timestamp_ms"] / 1000),
    )
    embed.set_footer(text=SERVER_SHORT_NAME)
    webhook.send(content=content, embed=embed, allowed_mentions=allowed_mentions)


def load_generic_hooks():
    """Load and validate all the subscribed log line webhooks from config.yml"""
    server_id = get_server_number()

    try:
        raw_config = get_config()["LOG_LINE_WEBHOOKS"]
    except KeyError:
        logger.error("No config.yml or no LOG_LINE_WEBHOOKS configuration")
        return

    for key, value in raw_config.items():
        if value:
            for field in value:
                validated_field = LogLineWebHookField(
                    url=field["URL"],
                    mentions=field["MENTIONS"],
                    servers=field["SERVERS"],
                )

                func = partial(
                    send_log_line_webhook_message,
                    validated_field.url,
                    validated_field.mentions,
                )

                # Have to set these attributes as the're used in LogLoop.process_hooks()
                func.__name__ = send_log_line_webhook_message.__name__
                func.__module__ = __name__

                on_generic(key, func)


load_generic_hooks()

if __name__ == "__main__":
    from rcon.settings import SERVER_INFO

    log = {
        "version": 1,
        "timestamp_ms": 1627734269000,
        "relative_time_ms": 221.212,
        "raw": "[543 ms (1627734269)] CONNECTED Dr.WeeD",
        "line_without_time": "CONNECTED Dr.WeeD",
        "action": "CONNECTED",
        "player": "Dr.WeeD",
        "steam_id_64_1": None,
        "player2": None,
        "steam_id_64_2": None,
        "weapon": None,
        "message": "Dr.WeeD",
        "sub_content": None,
    }
    real_vips(Rcon(SERVER_INFO), struct_log=log)
