from json.decoder import JSONDecodeError
import os, json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rcon.auto_settings import get_config, CONFIG_DIR

from .auth import login_required, api_response
from .utils import _get_data

@csrf_exempt
@login_required
def get_auto_settings(request):
    data = _get_data(request)
    server_number = data.get("server_number", os.getenv("SERVER_NUMBER"))

    config = get_config(f"auto_settings_{server_number}.json", silent=True)
    if not config:
        config = get_config("auto_settings.json", silent=True)
    if not config:
        config = get_config("auto_settings.default.json", silent=True)

    # Should the request fail if no (valid) auto settings are found?
    return api_response(
        result=config if config else dict(),
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
        return api_response(error="Invalid server number", status_code=400)
    
    settings = data.get("settings")
    if not settings:
        return api_response(error="No auto settings provided", status_code=400)

    try:
        # Check if valid JSON and indent for readability
        settings = json.loads(settings)
    except JSONDecodeError:
        return api_response(error="No valid JSON provided", status_code=400)

    with open(CONFIG_DIR+f'auto_settings_{server_number}.json', 'w+') as f:
        json.dump(settings, f, indent=2)

    return api_response(
        result=settings,
        command="set_auto_settings",
        arguments=dict(server_number=server_number),
        failed=False,
    )