import json
import logging

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt

import rcon.player_history as player_history
from rcon import player_history

from .audit_log import record_audit
from .auth import RconJsonResponse, login_required
from .decorators import require_content_type, require_http_methods
from .utils import _get_data

logger = logging.getLogger("rconweb")


@csrf_exempt
@login_required()
@permission_required("api.can_view_player_messages", raise_exception=True)
@require_http_methods(["GET"])
def get_player_messages(request):
    data = _get_data(request)
    res = None
    try:
        res = player_history.get_player_messages(player_id=data.get("player_id"))
        failed = False
    except:
        logger.exception("Unable to get player message history")
        failed = True

    return RconJsonResponse(
        {
            "result": res,
            "command": "player_messages",
            "arguments": data,
            "failed": failed,
        }
    )


@csrf_exempt
@login_required()
@permission_required("api.can_add_player_comments", raise_exception=True)
@require_http_methods(["POST"])
@require_content_type()
@record_audit
def post_player_comment(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.GET

    try:
        player_history.post_player_comment(
            player_id=data["player_id"],
            comment=data["comment"],
            user=request.user.username,
        )
        failed = False
    except:
        failed = True
        logger.exception("Unable to get player comments")

    return RconJsonResponse(
        {
            "result": None,
            "command": "post_player_comment",
            "arguments": data,
            "failed": failed,
        }
    )
