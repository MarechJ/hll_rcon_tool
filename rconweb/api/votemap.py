from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.vote_map import VoteMap

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import require_content_type
from .user_settings import _validate_user_config
from .utils import _get_data
from .views import audit

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
