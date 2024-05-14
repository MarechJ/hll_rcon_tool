import logging
import traceback
from typing import Sequence

from django.contrib.auth.decorators import permission_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import ApiKey, get_server_number

from .auth import AUTHORIZATION, login_required
from .decorators import require_content_type
from .utils import _get_data


def _forward_to_servers(
    path: str,
    request: HttpRequest,
    server_numbers: Sequence[int] | None = None,
    include_current: bool = False,
):
    all_api_keys = ApiKey()

    sessionid: str | None = request.COOKIES.get("sessionid")
    auth_header: str | None = request.headers.get(AUTHORIZATION)
    cookies = {"sessionid": sessionid} if sessionid else {}
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}

    for host in all_api_keys.get_all_keys().keys():
        server_number = host.split("_", 1)[-1]
        if server_number == get_server_number() and not include_current:
            continue

        if server_numbers is not None and int(server_number) not in server_numbers:
            continue

        url = f"http://{host}{path}"
        




@csrf_exempt
@login_required()
@permission_required("api.can_blacklist_players", raise_exception=True)
@require_content_type()
def do_blacklist_player(request):
    data = _get_data(request)
    command = data.get("command")
    if not command:
        res = 'Parameter "command" must not be none'
    else:
        try:
            res = rcon_api._str_request(command, can_fail=True, log_info=True)
        except CommandFailedError:
            res = "Command returned FAIL"
        except:
            logging.exception("Internal error when executing raw command")
            res = "Internal error!\n\n" + traceback.format_exc()
    return HttpResponse(res, content_type="text/plain")

@csrf_exempt
@login_required()
@permission_required("api.can_blacklist_players", raise_exception=True)
@require_content_type()
def apply_blacklist(request):

