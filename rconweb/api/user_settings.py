from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

from rcon.user_config.ban_tk_on_connect import BanTeamKillOnConnectUserConfig
from rcon.user_config.name_kicks import NameKickUserConfig
from rcon.user_config.rcon_settings import RconSettingsUserConfig
from rcon.user_config.steam import SteamUserConfig
from rcon.user_config.vac_game_bans import VacGameBansUserConfig

from .audit_log import record_audit
from .auth import api_response, login_required
from .utils import _get_data
from .views import _validate_user_config

logger = getLogger(__name__)


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
def get_rcon_settings_config(request):
    command_name = "get_rcon_settings_config"

    try:
        config = RconSettingsUserConfig.load_from_db()
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
# TODO: different permission?
@permission_required("api.", raise_exception=True)
def validate_rcon_settings_config(request):
    command_name = "validate_rcon_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconSettingsUserConfig, data=data, command_name=command_name, dry_run=True
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
def set_rcon_settings_config(request):
    command_name = "set_rcon_settings_config"
    data = _get_data(request)

    response = _validate_user_config(
        RconSettingsUserConfig, data=data, command_name=command_name, dry_run=False
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
        RconSettingsUserConfig, data=data, command_name=command_name, dry_run=False
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
