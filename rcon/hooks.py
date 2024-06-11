import logging
import re
from collections import defaultdict
from datetime import datetime
from functools import wraps
from threading import Timer
from typing import Final

from discord_webhook import DiscordEmbed

import rcon.steam_utils as steam_utils
from discord.utils import escape_markdown
from rcon.cache_utils import invalidates
from rcon.commands import CommandFailedError, HLLServerError
from rcon.discord import (
    dict_to_discord,
    get_prepared_discord_hooks,
    send_to_discord_audit,
)
from rcon.game_logs import (
    on_camera,
    on_chat,
    on_connected,
    on_disconnected,
    on_match_end,
    on_match_start,
)
from rcon.maps import UNKNOWN_MAP_NAME, parse_layer
from rcon.message_variables import format_message_string, populate_message_variables
from rcon.models import enter_session
from rcon.player_history import (
    _get_set_player,
    get_player,
    safe_save_player_action,
    save_end_player_session,
    save_player,
    save_start_player_session,
)
from rcon.rcon import Rcon, StructuredLogLineWithMetaData
from rcon.recent_actions import get_recent_actions
from rcon.types import (
    MessageVariableContext,
    MostRecentEvents,
    PlayerFlagType,
    RconInvalidNameActionType,
    SteamBansType,
    WindowsStoreIdActionType,
)
from rcon.user_config.camera_notification import CameraNotificationUserConfig
from rcon.user_config.chat_commands import (
    MESSAGE_VAR_RE,
    ChatCommandsUserConfig,
    chat_contains_command_word,
    is_command_word,
    is_description_word,
    is_help_word,
)
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.real_vip import RealVipUserConfig
from rcon.user_config.vac_game_bans import VacGameBansUserConfig
from rcon.user_config.webhooks import CameraWebhooksUserConfig
from rcon.utils import (
    DefaultStringFormat,
    MapsHistory,
    is_invalid_name_pineapple,
    is_invalid_name_whitespace,
)
from rcon.vote_map import VoteMap
from rcon.workers import record_stats_worker, temporary_broadcast, temporary_welcome

logger = logging.getLogger(__name__)


@on_chat
def count_vote(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
    enabled = VoteMap().handle_vote_command(rcon=rcon, struct_log=struct_log)
    if enabled and (match := re.match(r"\d\s*$", struct_log["sub_content"].strip())):
        rcon.message_player(
            player_id=struct_log["player_id_1"],
            message=f"INVALID VOTE\n\nUse: !votemap {match.group()}",
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


@on_chat
def chat_commands(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
    config = ChatCommandsUserConfig.load_from_db()
    if not config.enabled:
        return

    chat_message = struct_log["sub_content"]
    if chat_message is None:
        return

    event_cache = get_recent_actions()
    player_id: str = struct_log["player_id_1"]
    if player_id is None:
        return

    player_cache = event_cache.get(player_id, MostRecentEvents())
    chat_words = set(chat_message.split())
    for command in config.command_words:
        if not (
            triggered_word := chat_contains_command_word(
                chat_words, command.words, command.help_words
            )
        ):
            continue

        if is_command_word(triggered_word):
            message_vars: list[str] = re.findall(MESSAGE_VAR_RE, command.message)
            populated_variables = populate_message_variables(
                vars=message_vars, player_id=player_id
            )
            formatted_message = format_message_string(
                command.message,
                populated_variables=populated_variables,
                context={
                    MessageVariableContext.player_name.value: struct_log[
                        "player_name_1"
                    ],
                    MessageVariableContext.player_id.value: player_id,
                    MessageVariableContext.last_victim_player_id.value: player_cache.last_victim_player_id,
                    MessageVariableContext.last_victim_name.value: player_cache.last_victim_name,
                    MessageVariableContext.last_victim_weapon.value: player_cache.last_victim_weapon,
                    MessageVariableContext.last_nemesis_player_id.value: player_cache.last_nemesis_player_id,
                    MessageVariableContext.last_nemesis_name.value: player_cache.last_nemesis_name,
                    MessageVariableContext.last_nemesis_weapon.value: player_cache.last_nemesis_weapon,
                    MessageVariableContext.last_tk_nemesis_player_id.value: player_cache.last_tk_nemesis_player_id,
                    MessageVariableContext.last_tk_nemesis_name.value: player_cache.last_tk_nemesis_name,
                    MessageVariableContext.last_tk_nemesis_weapon.value: player_cache.last_tk_nemesis_weapon,
                    MessageVariableContext.last_tk_victim_player_id.value: player_cache.last_tk_victim_player_id,
                    MessageVariableContext.last_tk_victim_name.value: player_cache.last_tk_victim_name,
                    MessageVariableContext.last_tk_victim_weapon.value: player_cache.last_tk_victim_weapon,
                },
            )
            rcon.message_player(
                player_id=struct_log["player_id_1"],
                message=formatted_message,
                save_message=False,
            )
        # Help words describe a specific command
        elif is_help_word(triggered_word):
            description = command.description
            if description:
                rcon.message_player(
                    player_id=struct_log["player_id_1"],
                    message=description,
                    save_message=False,
                )
            else:
                rcon.message_player(
                    player_id=struct_log["player_id_1"],
                    message="Command description not set, let the admins know!",
                    save_message=False,
                )
                logger.warning(
                    "No descriptions set for chat command word(s), %s",
                    ", ".join(command.words),
                )

    # Description words trigger the entire help menu, test outside the loop
    # since these are global help words
    if is_description_word(chat_words, config.describe_words):
        description = config.describe_chat_commands()
        if description:
            rcon.message_player(
                player_id=struct_log["player_id_1"],
                message="\n".join(description),
                save_message=False,
            )
        else:
            logger.warning(
                "No descriptions set for command words, %s",
                ", ".join(config.describe_words),
            )


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
        with invalidates(Rcon.get_map, Rcon.get_next_map):
            try:
                # Don't use the current_map property and clear the cache to pull the new map name
                current_map = rcon.get_map()
            except (CommandFailedError, HLLServerError):
                current_map = parse_layer(UNKNOWN_MAP_NAME)
                logger.error(
                    "Unable to get current map, falling back to recording map as %s",
                    UNKNOWN_MAP_NAME,
                )

        guessed = True
        log_map_name = struct_log["sub_content"].rsplit(" ", 1)[0]
        log_time = datetime.fromtimestamp(struct_log["timestamp_ms"] / 1000)
        # Check that the log is less than 5min old
        if (datetime.utcnow() - log_time).total_seconds() < 5 * 60:
            # then we use the current map to be more accurate
            if current_map.map.name.lower() == log_map_name.lower():
                map_name_to_save = current_map
                guessed = False
            else:
                map_name_to_save = parse_layer(UNKNOWN_MAP_NAME)
                logger.warning(
                    "Got recent match start but map doesn't match %s != %s",
                    log_map_name,
                    current_map.map.name,
                )
        else:
            map_name_to_save = str(current_map)

        # TODO added guess - check if it's already in there - set prev end if None
        maps_history = MapsHistory()
        if len(maps_history) > 0:
            if maps_history[0]["end"] is None and maps_history[0]["name"]:
                maps_history.save_map_end(
                    old_map=maps_history[0]["name"],
                    end_timestamp=int(struct_log["timestamp_ms"] / 1000) - 100,
                )

        maps_history.save_new_map(
            new_map=str(map_name_to_save),
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
        current_map = rcon.current_map
    except (CommandFailedError, HLLServerError):
        current_map = parse_layer(UNKNOWN_MAP_NAME)
        logger.error(
            "Unable to get current map, falling back to recording map as %s",
            current_map,
        )

    # Log map names are inconsistently formatted but should match the map name that each Layer has
    log_map_name = struct_log["sub_content"]
    log_time = datetime.fromtimestamp(struct_log["timestamp_ms"] / 1000)

    # The log event loop can receive and process old log lines sometimes
    # Check to make sure that if we're processing an old logl ine
    if (datetime.utcnow() - log_time).total_seconds() < 60:
        # then we use the current map to be more accurate
        if current_map.map.name.lower() in log_map_name.lower():
            maps_history.save_map_end(
                str(current_map), end_timestamp=int(struct_log["timestamp_ms"] / 1000)
            )
        return

    # If we're processing an old match
    current_map = parse_layer(UNKNOWN_MAP_NAME)
    logger.info(f"Recording map end: {current_map}")
    maps_history.save_map_end(
        str(current_map), end_timestamp=int(struct_log["timestamp_ms"] / 1000)
    )


def ban_if_blacklisted(rcon: Rcon, player_id: str, name: str):
    with enter_session() as sess:
        player = get_player(sess, player_id)

        if not player:
            logger.error("Can't check blacklist, player not found %s", player_id)
            return

        if player.blacklist and player.blacklist.is_blacklisted:
            try:
                logger.info(
                    "Player %s was banned due blacklist, reason: %s",
                    str(name),
                    player.blacklist.reason,
                )
                rcon.perma_ban(
                    player_name=name,
                    reason=player.blacklist.reason,
                    by=f"BLACKLIST: {player.blacklist.by}",
                )
                safe_save_player_action(
                    rcon=rcon,
                    player_name=name,
                    action_type="PERMABAN",
                    reason=player.blacklist.reason,
                    by=f"BLACKLIST: {player.blacklist.by}",
                    player_id=player_id,
                )
                try:
                    send_to_discord_audit(
                        message=f"{dict_to_discord(dict(player=name, reason=player.blacklist.reason))}",
                        command_name="blacklist",
                        by="BLACKLIST",
                    )
                except:
                    logger.error("Unable to send blacklist to audit log")
            except:
                send_to_discord_audit(
                    message="Failed to apply ban on blacklisted players, please check the logs and report the error",
                    command_name="blacklist",
                    by="ERROR",
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


def ban_if_has_vac_bans(rcon: Rcon, player_id: str, name: str):
    config = VacGameBansUserConfig.load_from_db()

    max_days_since_ban = config.vac_history_days
    max_game_bans = (
        float("inf") if config.game_ban_threshhold <= 0 else config.game_ban_threshhold
    )
    whitelist_flags = config.whitelist_flags

    if max_days_since_ban <= 0:
        return  # Feature is disabled

    with enter_session() as sess:
        player = get_player(sess, player_id)

        if not player:
            logger.error("Can't check VAC history, player not found %s", player_id)
            return

        bans = player.steaminfo.bans if player.steaminfo else None
        if not bans or not isinstance(bans, dict):
            logger.warning(
                "Can't fetch Bans for player %s, received %s", player_id, bans
            )
            return

        if should_ban(
            bans,
            max_game_bans,
            max_days_since_ban,
            player_flags=player.flags,
            whitelist_flags=whitelist_flags,
        ):
            reason = config.ban_on_vac_history_reason.format(
                DAYS_SINCE_LAST_BAN=bans.get("DaysSinceLastBan"),
                MAX_DAYS_SINCE_BAN=str(max_days_since_ban),
            )
            logger.info(
                "Player %s was banned due VAC history, last ban: %s days ago",
                str(player),
                bans.get("DaysSinceLastBan"),
            )
            rcon.perma_ban(player_name=name, reason=reason, by="VAC BOT")

            try:
                audit_params = dict(
                    player=name,
                    player_id=player.player_id,
                    reason=reason,
                    days_since_last_ban=bans.get("DaysSinceLastBan"),
                    vac_banned=bans.get("VACBanned"),
                    number_of_game_bans=bans.get("NumberOfGameBans"),
                )
                send_to_discord_audit(
                    message=f"{dict_to_discord(audit_params)}",
                    command_name="blacklist",
                    by="VAC/GAME BAN",
                )
            except:
                logger.exception("Unable to send vac ban to audit log")


def inject_player_ids(func):
    @wraps(func)
    def wrapper(rcon, struct_log: StructuredLogLineWithMetaData):
        name = struct_log["player_name_1"]
        player_id = struct_log["player_id_1"]
        return func(rcon, struct_log, name, player_id)

    return wrapper


@on_connected()
@inject_player_ids
def handle_on_connect(
    rcon: Rcon, struct_log: StructuredLogLineWithMetaData, name: str, player_id: str
):
    try:
        rcon.get_players.cache_clear()
        rcon.get_player_info.clear_for(player=struct_log["player_name_1"])
    except Exception:
        logger.exception("Unable to clear cache for %s", player_id)

    timestamp = int(struct_log["timestamp_ms"]) / 1000
    if not player_id:
        logger.error(
            "Unable to get player ID for %s, can't process connection",
            struct_log,
        )
        return
    save_player(
        struct_log["player_name_1"],
        player_id,
        timestamp=int(struct_log["timestamp_ms"]) / 1000,
    )
    save_start_player_session(player_id, timestamp=timestamp)
    ban_if_blacklisted(rcon, player_id, struct_log["player_name_1"])
    ban_if_has_vac_bans(rcon, player_id, struct_log["player_name_1"])


@on_disconnected
@inject_player_ids
def handle_on_disconnect(rcon, struct_log, _, player_id: str):
    save_end_player_session(player_id, struct_log["timestamp_ms"] / 1000)


# Make the steam API call before the handle_on_connect hook so it's available for ban_if_blacklisted
@on_connected(0)
@inject_player_ids
def update_player_steaminfo_on_connect(
    rcon, struct_log: StructuredLogLineWithMetaData, _, player_id: str
):
    if not player_id:
        logger.error(
            "Can't update steam info, no steam id available for %s",
            struct_log.get("player_name_1"),
        )
        return

    logger.info(
        "Updating steam profile for player %s %s",
        struct_log["player_name_1"],
        struct_log["player_id_1"],
    )
    with enter_session() as sess:
        player = _get_set_player(
            sess, player_name=struct_log["player_name_1"], player_id=player_id
        )

        steam_utils.update_missing_old_steam_info_single_player(
            sess=sess, player=player
        )


pendingTimers: dict[str, list[tuple[RconInvalidNameActionType | None, Timer]]] = (
    defaultdict(list)
)


@on_connected()
@inject_player_ids
def windows_store_player_check(rcon: Rcon, _, name: str, player_id: str):
    config = RconServerSettingsUserConfig.load_from_db().windows_store_players

    if not config.enabled or steam_utils.is_steam_id_64(player_id):
        return

    action = config.action
    action_value = action.value if action else None

    logger.info(
        "Windows store player '%s' (%s) connected, action=%s",
        name,
        player_id,
        action_value,
    )

    try:
        send_to_discord_audit(
            message=config.audit_message.format_map(
                DefaultStringFormat(name=name, player_id=player_id, action=action_value)
            ),
            command_name=str(action_value),
        )
    except Exception:
        logger.exception(
            "Unable to send %s %s (%s) to audit", action_value, name, player_id
        )

    try:
        if action == WindowsStoreIdActionType.kick:
            rcon.kick(
                name,
                reason=config.player_message,
                by=config.audit_message_author,
                player_id=player_id,
            )
        elif action == WindowsStoreIdActionType.temp_ban:
            rcon.temp_ban(
                player_id=player_id,
                duration_hours=config.temp_ban_length_hours,
                reason=config.player_message,
                by=config.audit_message_author,
            )
        elif action == WindowsStoreIdActionType.perma_ban:
            rcon.perma_ban(
                player_id=player_id,
                reason=config.player_message,
                by=config.audit_message_author,
            )
    except Exception as e:
        logger.error(
            "Could not %s whitespace name player %s/%s: %s",
            action_value,
            name,
            player_id,
            e,
        )


@on_connected()
@inject_player_ids
def notify_invalid_names(rcon: Rcon, _, name: str, player_id: str):
    config = RconServerSettingsUserConfig.load_from_db().invalid_names

    if not config.enabled:
        return

    is_pineappple_name = is_invalid_name_pineapple(name)
    is_whitespace_name = is_invalid_name_whitespace(name)
    if not is_whitespace_name and not is_pineappple_name:
        return

    action = config.action
    action_value = action.value if action else None

    logger.info(
        "Player '%s' (%s) has an invalid name (ends in whitespace or multi byte unicode code point), action=%s",
        name,
        player_id,
        action_value,
    )

    try:
        send_to_discord_audit(
            message=config.audit_message.format_map(
                DefaultStringFormat(name=name, player_id=player_id, action=action_value)
            ),
            command_name=str(action_value),
        )
    except Exception:
        logger.exception(
            "Unable to send %s %s (%s) to audit", action_value, name, player_id
        )

    def notify_whitespace_player(action: RconInvalidNameActionType):
        if action is None:
            return
        elif action == RconInvalidNameActionType.kick:
            try:
                rcon.kick(
                    name,
                    reason=config.whitespace_name_player_message,
                    by=config.audit_message_author,
                    player_id=player_id,
                )
            except Exception as e:
                logger.error(
                    "Could not kick whitespace name player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )
        elif action == RconInvalidNameActionType.warn:
            try:
                rcon.message_player(
                    player_id=player_id,
                    message=config.whitespace_name_player_message,
                    by=config.audit_message_author,
                    save_message=False,
                )
            except Exception as e:
                logger.error(
                    "Could not message whitespace name player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )
        elif action == RconInvalidNameActionType.ban:
            try:
                rcon.temp_ban(
                    player_id=player_id,
                    reason=config.whitespace_name_player_message,
                    by=config.audit_message_author,
                    duration_hours=config.ban_length_hours,
                )
            except Exception as e:
                logger.error(
                    "Could not temp ban whitespace name player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )

    def notify_pineapple_player(action: RconInvalidNameActionType):
        if action is None:
            return
        elif action == RconInvalidNameActionType.kick:
            try:
                # TODO: it is not possible to kick pineapple names, remove them by banning/unbanning
                rcon.temp_ban(
                    player_id=player_id,
                    reason=config.pineapple_name_player_message,
                    by=config.audit_message_author,
                    duration_hours=1,
                )
            except Exception as e:
                logger.error(
                    "Could not temp ban (can't kick pineapple names) player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )
        elif action == RconInvalidNameActionType.warn:
            try:
                rcon.message_player(
                    player_id=player_id,
                    message=config.pineapple_name_player_message,
                    by=config.audit_message_author,
                    save_message=False,
                )
            except Exception as e:
                logger.error(
                    "Could not message pineapple name player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )
        elif action == RconInvalidNameActionType.ban:
            try:
                rcon.temp_ban(
                    player_id=player_id,
                    reason=config.pineapple_name_player_message,
                    by=config.audit_message_author,
                    duration_hours=config.ban_length_hours,
                )
            except Exception as e:
                logger.error(
                    "Could not temp ban player %s/%s: %s",
                    name,
                    player_id,
                    e,
                )

    # The player might not yet have finished connecting in order to action them.
    if is_whitespace_name:
        func = notify_whitespace_player
    else:
        func = notify_pineapple_player

    t = Timer(10, func, kwargs={"action": action})
    pendingTimers[player_id].append((action, t))
    t.start()

    # TODO: it is not possible to kick pineapple names, remove them by banning/unbanning
    if is_pineappple_name and action == RconInvalidNameActionType.kick:
        # Give the game server time to update bans so the ban can be removed automatically
        # and give the notify timer time to finish so the player is actually banned before
        # trying to remove it
        # players can't connect if they're banned so this should never fire and remove a
        # temp ban from any other reason unless there's another hook temp banning on connect
        t = Timer(15, rcon.remove_temp_ban, kwargs={"player_id": player_id})
        send_to_discord_audit(
            message=config.audit_kick_unban_message,
            command_name="kick",
            by=config.audit_message_author,
        )
        pendingTimers[player_id].append((action, t))
        t.start()


@on_disconnected
@inject_player_ids
def cleanup_pending_timers(rcon: Rcon, struct_log, name, player_id: str):
    """Cancel pending timers created by notify_player if the player disconnects

    Only messaging the player should be cancelled if they disconnect early
    Kicking players is non functional (RCON bug) so they're temp banned/pardoned
    Temporary banning players doesn't create a timer
    """
    pts: list[tuple[RconInvalidNameActionType | None, Timer]] = pendingTimers.pop(
        player_id, []
    )
    for action, pt in pts:
        # TODO: Can't kick pineapple names, don't cancel the thread if the ban removal is pending
        if action != RconInvalidNameActionType.kick and pt.is_alive():
            try:
                pt.cancel()
            except:
                pass


def _set_real_vips(rcon: Rcon, struct_log):
    config = RealVipUserConfig.load_from_db()
    if not config.enabled:
        logger.debug("Real VIP is disabled")
        return

    desired_nb_vips = config.desired_total_number_vips
    min_vip_slot = config.minimum_number_vip_slots
    vip_count = rcon.get_vips_count()

    remaining_vip_slots = max(desired_nb_vips - vip_count, max(min_vip_slot, 0))
    rcon.set_vip_slots_num(remaining_vip_slots)
    logger.info("Real VIP set slots to %s", remaining_vip_slots)


@on_connected()
def do_real_vips(rcon: Rcon, struct_log):
    _set_real_vips(rcon, struct_log)


@on_disconnected
def undo_real_vips(rcon: Rcon, struct_log):
    _set_real_vips(rcon, struct_log)


@on_camera
def notify_camera(rcon: Rcon, struct_log):
    send_to_discord_audit(
        command_name="camera", message=struct_log["message"], by="CRCON"
    )
    short_name: Final = RconServerSettingsUserConfig.load_from_db().short_name

    try:
        if hooks := get_prepared_discord_hooks(CameraWebhooksUserConfig):
            embeded = DiscordEmbed(
                title=f'{escape_markdown(struct_log["player_name_1"])}  - {escape_markdown(struct_log["player_id_1"])}',
                description=f'{short_name} - {struct_log["sub_content"]}',
                color=242424,
            )
            for h in hooks:
                h.add_embed(embeded)
                h.execute()
    except Exception:
        logger.exception("Unable to forward to hooks")

    config = CameraNotificationUserConfig.load_from_db()
    if config.broadcast:
        temporary_broadcast(rcon, struct_log["message"], 60)

    if config.welcome:
        temporary_welcome(rcon, struct_log["message"], 60)
