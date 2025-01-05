import json
import os

from django.views.decorators.csrf import csrf_exempt

from rcon.user_config.auto_settings import AutoSettingsConfig

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import permission_required, require_content_type, require_http_methods
from .multi_servers import forward_request
from .services import get_supervisor_client
from .utils import _get_data
from .views import audit

AUTO_SETTINGS_KEY_ORDER = [
    "always_apply_defaults",
    "can_invoke_multiple_rules",
    "defaults",
    "rules",
    "_available_settings",
    "_available_commands",
    "_available_conditions",
]
AUTO_SETTINGS_KEY_INDEX_MAP = {v: i for i, v in enumerate(AUTO_SETTINGS_KEY_ORDER)}


@csrf_exempt
@login_required()
@permission_required("api.can_view_auto_settings", raise_exception=True)
@require_http_methods(["GET"])
def get_auto_settings(request):
    data = _get_data(request)
    try:
        server_number = int(data.get("server_number", os.getenv("SERVER_NUMBER")))
    except ValueError:
        return api_response(error="Invalid server number", command="get_auto_settings")

    config = AutoSettingsConfig().get_settings()
    ordered_config = {
        k: v
        for (k, v) in sorted(
            config.items(),
            key=lambda pair: AUTO_SETTINGS_KEY_INDEX_MAP.get(
                pair[0], len(AUTO_SETTINGS_KEY_ORDER)
            ),
        )
    }

    return api_response(
        result=ordered_config,
        command="get_auto_settings",
        arguments=dict(server_number=server_number),
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_auto_settings", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def set_auto_settings(request):
    command_name = "set_auto_settings"
    data = _get_data(request)
    try:
        server_number = int(data.get("server_number", os.getenv("SERVER_NUMBER")))
    except ValueError:
        return api_response(error="Invalid server number", failed=True, status_code=400)
    do_restart_service = data.get("restart_service", True)
    do_forward = data.get("forward", False)
    if do_forward == "false" or do_forward == "0":
        do_forward = False
    if do_forward == "true" or do_forward == "1":
        do_forward = True
    if not isinstance(do_forward, bool):
        return api_response(error="forward needs to be a boolean value or empty", failed=True, status_code=400)

    settings = data.get("settings")
    if not settings:
        return api_response(error="No auto settings provided", command=command_name)

    try:
        # Check if valid JSON
        settings = json.loads(settings)
    except json.JSONDecodeError:
        return api_response(error="No valid JSON provided", command=command_name)

    audit(
        func_name=command_name,
        request=request,
        arguments={
            "server_number": server_number,
            "restart_service": do_restart_service,
            "forward": do_forward,
            "settings": json.dumps(settings),
        },
    )

    config = AutoSettingsConfig()
    config.set_settings(settings)

    if do_restart_service:
        client = get_supervisor_client()
        process = client.supervisor.getProcessInfo("auto_settings")
        if process["state"] == 20:  # The process is running
            client.supervisor.stopProcess("auto_settings")
            client.supervisor.startProcess("auto_settings")

    if do_forward:
        forward_request(request)

    return api_response(
        result=settings,
        command=command_name,
        arguments=dict(server_number=server_number, restart_service=do_restart_service),
        failed=False,
    )
