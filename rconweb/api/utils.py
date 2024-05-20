import json
from functools import wraps
from logging import getLogger
from typing import Any

from django.http.request import HttpRequest

from rcon.discord import send_to_discord_audit

logger = getLogger(__name__)


def _get_data(request: HttpRequest) -> dict[Any, Any] | Any:
    if request.method == "GET":
        parsed_get = {}

        # Allow passing lists of parameters, otherwise only the last value is captured
        # for instance without this api/get_recent_logs?filter_action=KILL&filter_action=CHAT
        # otherwise it would result in: filter_action = 'CHAT'
        # rather than: filter_action = ['KILL', 'CHAT']
        for key in request.GET.keys():
            v = request.GET.getlist(key)
            if len(v) == 1:
                v = v[0]
            parsed_get[key] = v

        return parsed_get
    # This is only used (currently) by the async_upload_vips endpoint which doesn't
    # include a parseable JSON body, but form data and it pulls the data itself
    elif request.method == "POST" and request.FILES:
        return {}
    else:
        # Don't silently swallow JSON parsing errors
        # login_required decorator will return a reasonable API response on failure
        # endpoints that don't require login should not be accepting POST requests
        return json.loads(request.body)


def allow_csv(endpoint):
    @wraps(endpoint)
    def wrapper(request, *args, **kwargs):
        to_csv = _get_data(request).get("to_csv")
        res = endpoint(request, *args, **kwargs)


# TODO: this isn't used anywhere
def audit(func_name, request, arguments):
    dont_audit = ["get_"]

    try:
        if any(func_name.startswith(s) for s in dont_audit):
            return
        args = dict(**arguments)
        try:
            del args["by"]
        except KeyError:
            pass
        arguments = " ".join([f"{k}: `{v}`" for k, v in args.items()])
        send_to_discord_audit(
            "`{}`: {}".format(func_name, arguments), request.user.username
        )
    except:
        logger.exception("Can't send audit log")
