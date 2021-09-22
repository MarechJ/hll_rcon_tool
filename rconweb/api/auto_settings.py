import os, json

from django.views.decorators.csrf import csrf_exempt
from rcon.user_config import AutoSettingsConfig

from .auth import login_required, api_response
from .utils import _get_data
from .multi_servers import forward_request
from .services import get_supervisor_client

AUTO_SETTINGS_KEY_ORDER = ["always_apply_defaults", "defaults", "rules", "_available_commands", "_available_conditions"]
AUTO_SETTINGS_KEY_INDEX_MAP = {v: i for i, v in enumerate(AUTO_SETTINGS_KEY_ORDER)}

@csrf_exempt
@login_required
def get_auto_settings(request):
    data = _get_data(request)
    try:
        server_number = int(data.get("server_number", os.getenv("SERVER_NUMBER")))
    except ValueError:
        return api_response(error="Invalid server number", command="get_auto_settings")

    config = AutoSettingsConfig().get_settings()
    ordered_config = {k: v for (k, v) in sorted(config.items(), key=lambda pair: AUTO_SETTINGS_KEY_INDEX_MAP[pair[0]])}

    return api_response(
        result=ordered_config,
        command="get_auto_settings",
        arguments=dict(server_number=server_number),
        failed=False,
    )

@csrf_exempt
@login_required
def set_auto_settings(request):
    data = _get_data(request)
    try:
        server_number = int(data.get("server_number", os.getenv("SERVER_NUMBER")))
    except ValueError:
        return api_response(error="Invalid server number", failed=True, status_code=400)
    do_restart_service = data.get("restart_service", True)
    do_forward = data.get("forward", False)
    
    settings = data.get("settings")
    if not settings:
        return api_response(error="No auto settings provided", command="set_auto_settings")

    try:
        # Check if valid JSON
        settings = json.loads(settings)
    except json.JSONDecodeError:
        return api_response(error="No valid JSON provided", command="set_auto_settings")

    config = AutoSettingsConfig()
    config.set_settings(settings)

    if do_restart_service:
        client = get_supervisor_client()
        process = client.supervisor.getProcessInfo('auto_settings')
        if process['state'] == 20: # The process is running
            client.supervisor.stopProcess('auto_settings')
            client.supervisor.startProcess('auto_settings')

    if do_forward:
        forward_request(request)

    return api_response(
        result=settings,
        command="set_auto_settings",
        arguments=dict(server_number=server_number, restart_service=do_restart_service),
        failed=False,
    )
