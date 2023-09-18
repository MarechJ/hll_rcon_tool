from logging import getLogger
from typing import Any, Type

import pydantic
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from rcon.user_config.auto_broadcast import AutoBroadcastUserConfig
from rcon.user_config.auto_kick import AutoVoteKickUserConfig
from rcon.user_config.auto_mod_level import AutoModLevelUserConfig
from rcon.user_config.auto_mod_no_leader import AutoModNoLeaderUserConfig
from rcon.user_config.auto_mod_seeding import AutoModSeedingUserConfig
from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.camera_notification import CameraNotificationUserConfig
from rcon.user_config.expired_vips import ExpiredVipsUserConfig
from rcon.user_config.gtx_server_name import ServerNameChangeUserConfig
from rcon.user_config.log_line_webhooks import LogLineWebhookUserConfig
from rcon.user_config.name_kicks import NameKickUserConfig
from rcon.user_config.rcon_connection_settings import RconConnectionSettingsUserConfig
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.user_config.scorebot import ScorebotUserConfig
from rcon.user_config.standard_messages import (
    StandardBroadcastMessagesUserConfig,
    StandardPunishmentMessagesUserConfig,
    StandardWelcomeMessagesUserConfig,
    get_all_message_types,
)
from rcon.user_config.steam import SteamUserConfig
from rcon.user_config.utils import BaseUserConfig, InvalidConfigurationError
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

from .audit_log import record_audit
from .auth import api_response, login_required
from .utils import _get_data

logger = getLogger(__name__)


def _validate_user_config(
    model: Type[BaseUserConfig],
    data: QueryDict | dict[str, Any],
    command_name: str,
    dry_run=True,
) -> JsonResponse | None:
    error_msg = None

    if "errors_as_json" in data:
        errors_as_json: bool = bool(data.pop("errors_as_json"))
    else:
        errors_as_json = False

    try:
        model.save_to_db(values=data, dry_run=dry_run)  # type: ignore
    except pydantic.ValidationError as e:
        if errors_as_json:
            error_msg = e.json()
        else:
            error_msg = str(e)

        logger.warning(error_msg)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )
    except InvalidConfigurationError as e:
        error_msg = str(e)
        logger.warning(error_msg)
        # logger.error(e)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )
    except Exception as e:
        error_msg = str(e)
        logger.exception(e)
        return api_response(
            command=command_name, failed=True, error=error_msg, arguments=data
        )


@csrf_exempt
@login_required()
@permission_required("api.can_view_auto_broadcast_config", raise_exception=True)
def get_auto_broadcasts_config(request):
    command_name = "get_auto_broadcasts_config"

    try:
        config = AutoBroadcastUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_auto_broadcasts_config(request):
    command_name = "describe_auto_broadcasts_config"
    return api_response(
        result=AutoBroadcastUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permissions?
@permission_required("api.can_change_auto_broadcast_config", raise_exception=True)
def validate_auto_broadcasts_config(request):
    command_name = "validate_auto_broadcasts_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoBroadcastUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_auto_broadcast_config", raise_exception=True)
@record_audit
def set_auto_broadcasts_config(request):
    command_name = "set_auto_broadcasts_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoBroadcastUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_votekick_autotoggle_config", raise_exception=True)
def get_votekick_autotoggle_config(request):
    command_name = "get_votekick_autotoggle_config"

    try:
        config = AutoVoteKickUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_votekick_autotoggle_config(request):
    command_name = "describe_votekick_autotoggle_config"

    return api_response(
        result=AutoVoteKickUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO different permission?
@permission_required("api.can_change_votekick_autotoggle_config", raise_exception=True)
def validate_votekick_autotoggle_config(request):
    command_name = "validate_votekick_autotoggle_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoVoteKickUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_votekick_autotoggle_config", raise_exception=True)
@record_audit
def set_votekick_autotoggle_config(request):
    command_name = "set_votekick_autotoggle_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoVoteKickUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_auto_mod_level_config(request):
    command_name = "get_auto_mod_level_config"

    try:
        config = AutoModLevelUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_auto_mod_level_config(request):
    command_name = "describe_auto_mod_level_config"

    return api_response(
        result=AutoModLevelUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_auto_mod_level_config(request):
    command_name = "validate_auto_mod_level_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModLevelUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_auto_mod_level_config(request):
    command_name = "set_auto_mod_level_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModLevelUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_auto_mod_no_leader_config(request):
    command_name = "get_auto_mod_no_leader_config"

    try:
        config = AutoModNoLeaderUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_auto_mod_no_leader_config(request):
    command_name = "describe_auto_mod_no_leader_config"

    return api_response(
        result=AutoModNoLeaderUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_auto_mod_no_leader_config(request):
    command_name = "validate_auto_mod_no_leader_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModNoLeaderUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_auto_mod_no_leader_config(request):
    command_name = "set_auto_mod_no_leader_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModNoLeaderUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_auto_mod_seeding_config(request):
    command_name = "get_auto_mod_seeding_config"

    try:
        config = AutoModSeedingUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_auto_mod_seeding_config(request):
    command_name = "describe_auto_mod_seeding_config"

    return api_response(
        result=AutoModSeedingUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_auto_mod_seeding_config(request):
    command_name = "validate_auto_mod_seeding_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModSeedingUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_auto_mod_seeding_config(request):
    command_name = "set_auto_mod_seeding_config"
    data = _get_data(request)

    response = _validate_user_config(
        AutoModSeedingUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_tk_ban_on_connect_config(request):
    command_name = "get_tk_ban_on_connect_config"

    try:
        config = BanTeamKillOnConnectUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_tk_ban_on_connect_config(request):
    command_name = "describe_tk_ban_on_connect_config"

    return api_response(
        result=BanTeamKillOnConnectUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_tk_ban_on_connect_config(request):
    command_name = "validate_tk_ban_on_connect_config"
    data = _get_data(request)

    response = _validate_user_config(
        BanTeamKillOnConnectUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_tk_ban_on_connect_config(request):
    command_name = "set_tk_ban_on_connect_config"
    data = _get_data(request)

    response = _validate_user_config(
        BanTeamKillOnConnectUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_camera_config", raise_exception=True)
def get_camera_notification_config(request):
    command_name = "get_camera_notification_config"

    try:
        config = CameraNotificationUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_camera_notification_config(request):
    command_name = "describe_camera_notification_config"

    return api_response(
        result=CameraNotificationUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.can_change_camera_config", raise_exception=True)
def validate_camera_notification_config(request):
    command_name = "validate_camera_notification_config"
    data = _get_data(request)

    response = _validate_user_config(
        CameraNotificationUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_camera_config", raise_exception=True)
@record_audit
def set_camera_notification_config(request):
    command_name = "set_camera_notification_config"
    data = _get_data(request)

    response = _validate_user_config(
        CameraNotificationUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_expired_vip_config(request):
    command_name = "get_expired_vip_config"

    try:
        config = ExpiredVipsUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_expired_vip_config(request):
    command_name = "describe_expired_vip_config"

    return api_response(
        result=ExpiredVipsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_expired_vip_config(request):
    command_name = "validate_expired_vip_config"
    data = _get_data(request)

    response = _validate_user_config(
        ExpiredVipsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_expired_vip_config(request):
    command_name = "set_expired_vip_config"
    data = _get_data(request)

    response = _validate_user_config(
        ExpiredVipsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_server_name_change_config(request):
    command_name = "get_server_name_change_config"

    try:
        config = ServerNameChangeUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_server_name_change_config(request):
    command_name = "describe_server_name_change_config"

    return api_response(
        result=ServerNameChangeUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_server_name_change_config(request):
    command_name = "validate_server_name_change_config"
    data = _get_data(request)

    response = _validate_user_config(
        ServerNameChangeUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_server_name_change_config(request):
    command_name = "set_server_name_change_config"
    data = _get_data(request)

    response = _validate_user_config(
        ServerNameChangeUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_log_line_webhook_config(request):
    command_name = "get_log_line_webhook_config"

    try:
        config = LogLineWebhookUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_log_line_webhook_config(request):
    command_name = "describe_log_line_webhook_config"

    return api_response(
        result=LogLineWebhookUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_log_line_webhook_config(request):
    command_name = "validate_log_line_webhook_config"
    data = _get_data(request)

    response = _validate_user_config(
        LogLineWebhookUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_log_line_webhook_config(request):
    command_name = "set_log_line_webhook_config"
    data = _get_data(request)

    response = _validate_user_config(
        LogLineWebhookUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_name_kick_config(request):
    command_name = "get_name_kick_config"

    try:
        config = NameKickUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_name_kick_config(request):
    command_name = "describe_name_kick_config"

    return api_response(
        result=NameKickUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_name_kick_config(request):
    command_name = "validate_name_kick_config"
    data = _get_data(request)

    response = _validate_user_config(
        NameKickUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_name_kick_config(request):
    command_name = "set_name_kick_config"
    data = _get_data(request)

    response = _validate_user_config(
        NameKickUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_rcon_connection_settings_config(request):
    command_name = "get_rcon_connection_settings_config"

    try:
        config = RconConnectionSettingsUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_rcon_connection_settings_config(request):
    command_name = "describe_rcon_connection_settings_config"

    return api_response(
        result=RconConnectionSettingsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_rcon_connection_settings_config(request):
    command_name = "validate_rcon_connection_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconConnectionSettingsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_rcon_connection_settings_config(request):
    command_name = "set_rcon_connection_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconConnectionSettingsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_rcon_server_settings_config(request):
    command_name = "get_rcon_server_settings_config"

    try:
        config = RconServerSettingsUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_rcon_server_settings_config(request):
    command_name = "describe_rcon_server_settings_config"

    return api_response(
        result=RconServerSettingsUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_rcon_server_settings_config(request):
    command_name = "validate_rcon_server_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconServerSettingsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_rcon_server_settings_config(request):
    command_name = "set_rcon_server_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconServerSettingsUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_scorebot_config(request):
    command_name = "get_scorebot_config"

    try:
        config = ScorebotUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
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
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_scorebot_config(request):
    command_name = "validate_scorebot_config"
    data = _get_data(request)

    response = _validate_user_config(
        ScorebotUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_scorebot_config(request):
    command_name = "set_scorebot_config"
    data = _get_data(request)

    response = _validate_user_config(
        ScorebotUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_broadcast_messages", raise_exception=True)
def get_standard_broadcast_messages(request):
    command_name = "get_standard_broadcast_messages"

    try:
        config = StandardBroadcastMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_standard_broadcast_messages(request):
    command_name = "describe_standard_broadcast_messages"

    return api_response(
        result=StandardBroadcastMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_broadcast_messages", raise_exception=True)
def validate_standard_broadcast_messages(request):
    command_name = "validate_standard_broadcast_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardBroadcastMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_broadcast_messages", raise_exception=True)
def set_standard_broadcast_messages(request):
    command_name = "set_standard_broadcast_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardBroadcastMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_punishment_messages", raise_exception=True)
def get_standard_punishments_messages(request):
    command_name = "get_standard_punishments_messages"

    try:
        config = StandardPunishmentMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_standard_punishments_messages(request):
    command_name = "describe_standard_punishments_messages"

    return api_response(
        result=StandardPunishmentMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required(
    "api.can_change_standard_punishment_messages", raise_exception=True
)
def validate_standard_punishments_messages(request):
    command_name = "validate_standard_punishments_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardPunishmentMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required(
    "api.can_change_standard_punishment_messages", raise_exception=True
)
def set_standard_punishments_messages(request):
    command_name = "set_standard_punishments_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardPunishmentMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_standard_welcome_messages", raise_exception=True)
def get_standard_welcome_messages(request):
    command_name = "get_standard_welcome_messages"

    try:
        config = StandardWelcomeMessagesUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_standard_welcome_messages(request):
    command_name = "describe_standard_welcome_messages"

    return api_response(
        result=StandardWelcomeMessagesUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_welcome_messages", raise_exception=True)
def validate_standard_welcome_messages(request):
    command_name = "validate_standard_welcome_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardWelcomeMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_standard_welcome_messages", raise_exception=True)
def set_standard_welcome_messages(request):
    command_name = "set_standard_welcome_messages"
    data = _get_data(request)

    response = _validate_user_config(
        StandardWelcomeMessagesUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_steam_config(request):
    command_name = "get_steam_config"

    try:
        config = SteamUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_steam_config(request):
    command_name = "describe_steam_config"

    return api_response(
        result=SteamUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_steam_config(request):
    command_name = "validate_steam_config"
    data = _get_data(request)

    response = _validate_user_config(
        SteamUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_steam_config(request):
    command_name = "set_steam_config"
    data = _get_data(request)

    response = _validate_user_config(
        SteamUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_vac_game_bans_config(request):
    command_name = "get_vac_game_bans_config"

    try:
        config = VacGameBansUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_vac_game_bans_config(request):
    command_name = "describe_vac_game_bans_config"

    return api_response(
        result=VacGameBansUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_vac_game_bans_config(request):
    command_name = "validate_vac_game_bans_config"
    data = _get_data(request)

    response = _validate_user_config(
        VacGameBansUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_vac_game_bans_config(request):
    command_name = "set_vac_game_bans_config"
    data = _get_data(request)

    response = _validate_user_config(
        VacGameBansUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_admin_pings_discord_webhooks_config(request):
    command_name = "get_admin_pings_discord_webhooks_config"

    try:
        config = AdminPingWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_admin_pings_discord_webhooks_config(request):
    command_name = "describe_admin_pings_discord_webhooks_config"

    return api_response(
        result=AdminPingWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_admin_pings_discord_webhooks_config(request):
    command_name = "validate_admin_pings_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        AdminPingWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_admin_pings_discord_webhooks_config(request):
    command_name = "set_admin_pings_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        AdminPingWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_audit_discord_webhooks_config(request):
    command_name = "get_audit_webhooks_config"

    try:
        config = AuditWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_audit_discord_webhooks_config(request):
    command_name = "describe_audit_discord_webhooks_config"

    return api_response(
        result=AuditWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_audit_discord_webhooks_config(request):
    command_name = "validate_audit_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        AuditWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_audit_discord_webhooks_config(request):
    command_name = "set_audit_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        AuditWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_camera_discord_webhooks", raise_exception=True)
def get_camera_discord_webhooks_config(request):
    command_name = "get_camera_discord_webhooks"

    try:
        config = CameraWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_camera_discord_webhooks_config(request):
    command_name = "describe_camera_discord_webhooks_config"

    return api_response(
        result=CameraWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_camera_discord_webhooks", raise_exception=True)
def validate_camera_discord_webhooks_config(request):
    command_name = "validate_camera_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        CameraWebhooksUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_camera_discord_webhooks", raise_exception=True)
def set_camera_discord_webhooks_config(request):
    command_name = "set_camera_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        CameraWebhooksUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_chat_discord_webhooks_config(request):
    command_name = "get_chat_webhooks_config"

    try:
        config = ChatWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_chat_discord_webhooks_config(request):
    command_name = "describe_chat_discord_webhooks_config"

    return api_response(
        result=ChatWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_chat_discord_webhooks_config(request):
    command_name = "validate_chat_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        ChatWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_chat_discord_webhooks_config(request):
    command_name = "set_chat_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        ChatWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
def get_kills_discord_webhooks_config(request):
    command_name = "get_kills_webhooks_config"

    try:
        config = KillsWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_kills_discord_webhooks_config(request):
    command_name = "describe_kills_discord_webhooks_config"

    return api_response(
        result=KillsWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_kills_discord_webhooks_config(request):
    command_name = "get_kills_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        KillsWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=True,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.", raise_exception=True)
@record_audit
def set_kills_discord_webhooks_config(request):
    command_name = "set_kills_webhooks_config"
    data = _get_data(request)

    response = _validate_user_config(
        KillsWebhooksUserConfig,
        data=data,
        command_name=command_name,
        dry_run=False,
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_view_watchlist_discord_webhooks", raise_exception=True)
def get_watchlist_discord_webhooks(request):
    command_name = "get_watchlist_discord_webhooks"

    try:
        config = WatchlistWebhooksUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
def describe_watchlist_discord_webhooks(request):
    command_name = "describe_watchlist_discord_webhooks"

    return api_response(
        result=WatchlistWebhooksUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_watchlist_discord_webhooks", raise_exception=True)
def validate_watchlist_discord_webhooks(request):
    command_name = "validate_watchlist_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        WatchlistWebhooksUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
# TODO: permission does not exist yet
@permission_required("api.can_change_watchlist_discord_webhooks", raise_exception=True)
def set_watchlist_discord_webhooks(request):
    command_name = "set_watchlist_discord_webhooks"
    data = _get_data(request)

    response = _validate_user_config(
        WatchlistWebhooksUserConfig, data=data, command_name=command_name, dry_run=False
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_discord_webhooks", raise_exception=True)
def get_all_discord_webhooks(request):
    command_name = "get_all_discord_webhooks"

    error_msg = None
    try:
        hooks = get_all_hook_types(as_dict=True)
        return api_response(result=hooks, command=command_name, failed=False)
    except Exception as e:
        error_msg = str(e)
        return api_response(command=command_name, error=error_msg)
