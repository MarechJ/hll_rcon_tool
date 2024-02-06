import json
from copy import copy
from logging import getLogger
from typing import Any, Type

import pydantic
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import discord
from rcon.user_config.real_vip import RealVipUserConfig
from rcon.discord import send_to_discord_audit
from rcon.types import InvalidLogTypeError
from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig
from rcon.user_config.auto_mod_solo_tank import AutoModNoSoloTankUserConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.camera_notification import CameraNotificationUserConfig
from rcon.user_config.chat_commands import ChatCommandsUserConfig
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.user_config.gtx_server_name import GtxServerNameChangeUserConfig
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.name_kicks import NameKickUserConfig
from rcon.user_config.rcon_connection_settings import RconConnectionSettingsUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.scorebot import ScorebotUserConfig
from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.user_config.standard_messages import (
    StandardBroadcastMessagesUserConfig,
    StandardPunishmentMessagesUserConfig,
    StandardWelcomeMessagesUserConfig,
    get_all_message_types,
)
from rcon.user_config.steam import SteamUserConfig
from rcon.user_config.utils import (
    DISCORD_AUDIT_FORMAT,
    BaseUserConfig,
    InvalidKeysConfigurationError,
    set_user_config,
)
from rcon.user_config.vac_game_bans import VacGameBansUserConfig
from rcon.user_config.webhooks import (
    AdminPingWebhooksUserConfig,
    AuditWebhooksUserConfig,
    CameraWebhooksUserConfig,
    ChatWebhooksUserConfig,
    KillsWebhooksUserConfig,
    WatchlistWebhooksUserConfig,
    get_all_hook_types,
)
from rcon.utils import dict_differences

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import require_content_type
from .utils import _get_data

logger = getLogger(__name__)


def _validate_user_config(
    model: Type[BaseUserConfig],
    data: QueryDict | dict[str, Any],
    command_name: str,
    dry_run=True,
) -> JsonResponse | None:
    error_msg = None

    # Make a copy for responses, but remove keys from data
    # so they aren't registered as extra keys and generate
    # InvalidKeysConfigurationError exceptions
    arguments = copy(data)
    if "errors_as_json" in data:
        errors_as_json: bool = bool(data.pop("errors_as_json"))
    else:
        errors_as_json = False

    if "reset_to_default" in data:
        reset_to_default: bool = bool(data.pop("reset_to_default"))
    else:
        reset_to_default = False

    if reset_to_default:
        try:
            default = model()
            result = default.model_dump()
            set_user_config(default.KEY(), result)
            return api_response(
                command=command_name,
                failed=False,
                result=result,
                arguments=arguments,
            )
        except pydantic.ValidationError as e:
            if errors_as_json:
                error_msg = e.json()
            else:
                error_msg = str(e)
            logger.warning(error_msg)
            return api_response(
                command=command_name, failed=True, error=error_msg, arguments=arguments
            )
        except Exception as e:
            error_msg = str(e)
            logger.exception(e)
            return api_response(
                command=command_name, failed=True, error=error_msg, arguments=arguments
            )

    try:
        model.save_to_db(values=data, dry_run=dry_run)  # type: ignore
    except pydantic.ValidationError as e:
        if errors_as_json:
            error_msg = e.json()
        else:
            error_msg = str(e)
        logger.warning(error_msg)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=arguments
        )
    except (InvalidKeysConfigurationError, InvalidLogTypeError) as e:
        if errors_as_json:
            error_msg = json.dumps([e.asdict()])
        else:
            error_msg = str(e)
        logger.warning(error_msg)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=arguments
        )
    except Exception as e:
        error_msg = str(e)
        logger.exception(e)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=arguments
        )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_votemap_config(request):
    command_name = "get_votemap_config"

    return api_response(
        result=VoteMapUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_auto_broadcasts_config(request):
    command_name = "describe_auto_broadcasts_config"
    return api_response(
        result=AutoBroadcastUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_votekick_autotoggle_config(request):
    command_name = "describe_votekick_autotoggle_config"

    return api_response(
        result=AutoVoteKickUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_auto_mod_level_config(request):
    command_name = "describe_auto_mod_level_config"

    return api_response(
        result=AutoModLevelUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_auto_mod_no_leader_config(request):
    command_name = "describe_auto_mod_no_leader_config"

    return api_response(
        result=AutoModNoLeaderUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_auto_mod_seeding_config(request):
    command_name = "describe_auto_mod_seeding_config"

    return api_response(
        result=AutoModSeedingUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_auto_mod_solo_tank_config(request):
    command_name = "describe_auto_mod_solo_tank_config"

    return api_response(
        result=AutoModNoSoloTankUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_tk_ban_on_connect_config(request):
    command_name = "describe_tk_ban_on_connect_config"

    return api_response(
        result=BanTeamKillOnConnectUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_camera_notification_config(request):
    command_name = "describe_camera_notification_config"

    return api_response(
        result=CameraNotificationUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_expired_vip_config(request):
    command_name = "describe_expired_vip_config"

    return api_response(
        result=ExpiredVipsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_server_name_change_config(request):
    command_name = "describe_server_name_change_config"

    return api_response(
        result=GtxServerNameChangeUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_log_line_webhook_config(request):
    command_name = "describe_log_line_webhook_config"

    return api_response(
        result=LogLineWebhookUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_name_kick_config(request):
    command_name = "describe_name_kick_config"

    return api_response(
        result=NameKickUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_rcon_connection_settings_config(request):
    command_name = "describe_rcon_connection_settings_config"

    return api_response(
        result=RconConnectionSettingsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_rcon_server_settings_config(request):
    command_name = "describe_rcon_server_settings_config"

    return api_response(
        result=RconServerSettingsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_scorebot_config(request):
    command_name = "describe_scorebot_config"

    try:
        config = ScorebotUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=ScorebotUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_standard_broadcast_messages(request):
    command_name = "describe_standard_broadcast_messages"

    return api_response(
        result=StandardBroadcastMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_standard_punishments_messages(request):
    command_name = "describe_standard_punishments_messages"

    return api_response(
        result=StandardPunishmentMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_standard_welcome_messages(request):
    command_name = "describe_standard_welcome_messages"

    return api_response(
        result=StandardWelcomeMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required(
    {
        "api.can_view_standard_broadcast_messages",
        "api.can_view_standard_punishment_messages",
        "api.can_view_standard_welcome_messages",
    }
)
@require_http_methods(["GET"])
def get_all_standard_message_config(request):
    command_name = "get_all_standard_message_config"

    try:
        res = get_all_message_types(as_dict=True)
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=res,
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_steam_config(request):
    command_name = "describe_steam_config"

    return api_response(
        result=SteamUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_vac_game_bans_config(request):
    command_name = "describe_vac_game_bans_config"

    return api_response(
        result=VacGameBansUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_admin_pings_discord_webhooks_config(request):
    command_name = "describe_admin_pings_discord_webhooks_config"

    return api_response(
        result=AdminPingWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_audit_discord_webhooks_config(request):
    command_name = "describe_audit_discord_webhooks_config"

    return api_response(
        result=AuditWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_camera_discord_webhooks_config(request):
    command_name = "describe_camera_discord_webhooks_config"

    return api_response(
        result=CameraWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_chat_discord_webhooks_config(request):
    command_name = "describe_chat_discord_webhooks_config"

    return api_response(
        result=ChatWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_kills_discord_webhooks_config(request):
    command_name = "describe_kills_discord_webhooks_config"

    return api_response(
        result=KillsWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_watchlist_discord_webhooks_config(request):
    command_name = "describe_watchlist_discord_webhooks"

    return api_response(
        result=WatchlistWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_chat_commands_config(request):
    command_name = "describe_chat_commands_config"

    return api_response(
        result=ChatCommandsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required(
    {
        "api.can_view_admin_pings_discord_webhooks_config",
        "api.can_view_audit_discord_webhooks_config",
        "api.can_view_camera_discord_webhooks_config",
        "api.can_view_chat_discord_webhooks_config",
        "api.can_view_kills_discord_webhooks_config",
        "api.can_view_watchlist_discord_webhooks_config",
    },
    raise_exception=True,
)
@require_http_methods(["GET"])
def get_all_discord_webhooks_config(request):
    command_name = "get_all_discord_webhooks"

    error_msg = None
    try:
        hooks = get_all_hook_types(as_dict=True)
        return api_response(result=hooks, command=command_name, failed=False)
    except Exception as e:
        error_msg = str(e)
        return api_response(command=command_name, error=error_msg)


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_real_vip_config(request):
    command_name = "describe_real_vip_config"

    return api_response(
        result=RealVipUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )
