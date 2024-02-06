from logging import getLogger

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon.user_config.vote_map import VoteMapUserConfig

from .auth import api_response, login_required

logger = getLogger(__name__)


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_votemap_config(request):
    command_name = "describe_votemap_config"

    return api_response(
        result=VoteMapUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )
