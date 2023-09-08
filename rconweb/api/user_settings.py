from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

from rcon.user_config.steam import SteamUserConfig

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
