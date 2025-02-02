import datetime
import logging

from pydantic import HttpUrl

from rcon.blacklist import blacklist_or_ban
from rcon.discord import send_to_discord_audit
from rcon.game_logs import get_recent_logs
from rcon.logs.loop import on_tk
from rcon.player_history import get_player_profile, player_has_flag
from rcon.rcon import Rcon
from rcon.types import StructuredLogLineWithMetaData, BlacklistRecordWithBlacklistType
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig

logger = logging.getLogger(__name__)


def is_player_death(player, log):
    return log["action"] == "KILL" and player == log["player_name_2"]


def is_player_kill(player, log):
    return log["action"] == "KILL" and player == log["player_name_1"]


@on_tk
def auto_ban_if_tks_right_after_connection(
        rcon: Rcon,
        log: StructuredLogLineWithMetaData,
        config: BanTeamKillOnConnectUserConfig | None = None,
) -> None | BlacklistRecordWithBlacklistType:
    if config is None:
        config = BanTeamKillOnConnectUserConfig.load_from_db()
    if not config or not config.enabled:
        return

    result: None | BlacklistRecordWithBlacklistType = None

    player_name = log["player_name_1"]
    player_id = log["player_id_1"]
    player_profile = None
    vips = {}
    try:
        player_profile = get_player_profile(player_id, 0)
    except:
        logger.exception("Unable to get player profile")
    try:
        vips = set(v["player_id"] for v in rcon.get_vip_ids())
    except:
        logger.exception("Unable to get VIPS")

    last_logs = get_recent_logs(
        end=500, player_search=player_name, exact_player_match=True
    )
    logger.debug("Checking TK from %s", player_name)
    author = config.author_name
    reason = config.message
    discord_msg = config.discord_webhook_message
    webhook = config.discord_webhook_url
    max_time_minute = config.max_time_after_connect_minutes
    excluded_weapons = [w.lower() for w in config.excluded_weapons]
    ignore_after_kill = config.ignore_tk_after_n_kills
    ignore_after_death = config.ignore_tk_after_n_deaths
    whitelist_players = config.whitelist_players
    tk_tolerance_count = config.teamkill_tolerance_count

    if player_profile:
        if whitelist_players.is_vip and player_id in vips:
            logger.debug("Not checking player because he's VIP")
            return

        if (
                whitelist_players.has_at_least_n_sessions != 0
                and player_profile["sessions_count"]
                >= whitelist_players.has_at_least_n_sessions
        ):
            logger.debug(
                "Not checking player because he has %s sessions",
                player_profile["sessions_count"],
            )
            return

        for f in whitelist_players.has_flag:
            if player_has_flag(player_profile, f):
                logger.debug("Not checking player because he has flag %s", f)
                return

    last_action_is_connect = False
    last_connect_time = None
    kill_counter = 0
    death_counter = 0
    tk_counter = 0
    for log in reversed(last_logs["logs"]):
        logger.debug(log)

        if log["action"] == "CONNECTED":
            last_action_is_connect = log
            last_connect_time = log["timestamp_ms"]
            kill_counter = 0
            death_counter = 0
            continue
        if (
                log["action"] == "TEAM KILL"
                and log["player_name_1"] == player_name
                and last_action_is_connect
        ):
            if excluded_weapons and log["weapon"].lower() in excluded_weapons:
                logger.debug("Not counting TK as offense due to weapon exclusion")
                continue
            if log["timestamp_ms"] - last_connect_time > max_time_minute * 60 * 1000:
                logger.debug(
                    "Not counting TK as offense due to elapsed time exclusion, last connection time %s, tk time %s",
                    datetime.datetime.fromtimestamp(last_connect_time / 1000),
                    datetime.datetime.fromtimestamp(log["timestamp_ms"] / 1000),
                )
                continue

            tk_counter += 1
            if tk_counter > tk_tolerance_count:
                logger.info(
                    "Banning player %s for TEAMKILL after connect %s", player_name, log
                )
                if config.ban_duration.total_seconds > 0:
                    expires_at = (
                            datetime.datetime.now() + config.ban_duration.as_timedelta
                    )
                else:
                    expires_at = None

                result = blacklist_or_ban(
                    rcon=rcon,
                    blacklist_id=config.blacklist_id,
                    player_id=player_id,
                    reason=reason,
                    admin_name=author,
                    expires_at=expires_at,
                )
                logger.info(
                    "Banned player %s for TEAMKILL after connect %s", player_name, log
                )

                webhookurls: list[HttpUrl | None] | None
                if webhook is None:
                    webhookurls = None
                else:
                    webhookurls = [webhook]
                send_to_discord_audit(
                    message=discord_msg.format(player=player_name),
                    command_name="blacklist",
                    by=author,
                    webhookurls=webhookurls,
                )
        elif is_player_death(player_name, log):
            death_counter += 1
            if death_counter >= ignore_after_death:
                last_action_is_connect = False
        elif is_player_kill(player_name, log):
            kill_counter += 1
            if kill_counter >= ignore_after_kill:
                last_action_is_connect = False

    return result
