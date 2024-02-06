import json
import logging
from copy import deepcopy
from typing import Any

import requests
from django.contrib.auth.decorators import permission_required
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon.utils import ApiKey

from .auth import AUTHORIZATION, api_response, login_required

logger = logging.getLogger("rcon")


@login_required()
@permission_required("api.can_view_other_crcon_servers", raise_exception=True)
@csrf_exempt
@require_http_methods(["GET"])
def get_server_list(request):
    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    logger.debug(keys)
    names = []
    for host, key in keys.items():
        if key == my_key:
            continue
        url = f"http://{host}/api/get_connection_info"
        try:
            res = requests.get(
                url,
                timeout=5,
                cookies=dict(sessionid=request.COOKIES.get("sessionid")),
            )
            if res.ok:
                names.append(res.json()["result"])
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {url}")

    return api_response(names, failed=False, command="server_list")


def forward_request(request):
    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    sessionid: str | None = request.COOKIES.get("sessionid")
    auth_header: str | None = request.headers.get(AUTHORIZATION)
    cookies = {"sessionid": sessionid} if sessionid else {}
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}

    results = []
    for host, key in keys.items():
        if key == my_key:
            continue
        try:
            url = f"http://{host}{request.path}"

            params = dict(request.GET)
            params.pop("forward", None)
            try:
                data = json.loads(request.body)
                data.pop("forward", None)
            except json.JSONDecodeError as e:
                logger.error("JSON parse error %s: %s", request.path, e)
                data = None
            logger.info("Forwarding request: %s %s %s", url, params, data)
            res = requests.post(
                url,
                params=params,
                json=data,
                timeout=5,
                cookies=cookies,
                headers=headers,
            )
            # Automatically retry HttpResponseNotAllowed errors as GET requests
            if res.status_code == 405:
                res = requests.get(
                    url,
                    params=params,
                    json=data,
                    timeout=5,
                    cookies=cookies,
                    headers=headers,
                )

            if res.ok:
                r = {"host": host, "response": res.json()}
                results.append(r)
                logger.info(r)
            else:
                # todo add failure to results
                logger.warning(f"Forwarding to {host} failed %s", res.text)
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {url=}")

    return results


def forward_command(
    path: str,
    sessionid: str | None,
    auth_header: str | None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | QueryDict | None = None,
):
    server_api_key = ApiKey()
    keys = server_api_key.get_all_keys()
    my_key = server_api_key.get_key()
    params = deepcopy(params) or {}
    data = deepcopy(json) or {}
    cookies = {"sessionid": sessionid} if sessionid else {}
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}
    results = []

    if "forwarded" in params or "forwarded" in data:
        logger.debug("The request was already forwarded")
        return []
    if params:
        params.pop("forward", None)
        params["forwarded"] = True
    if data:
        data.pop("forward", None)
        data["forwarded"] = True

    for host, key in keys.items():
        if key == my_key:
            continue
        try:
            url = f"http://{host}{path}"

            logger.info("Forwarding command: %s %s %s", url, params, data)
            res = requests.post(
                url,
                params=params,
                json=data,
                timeout=5,
                cookies=cookies,
                headers=headers,
            )
            # Automatically retry HttpResponseNotAllowed errors as GET requests
            if res.status_code == 405:
                res = requests.get(
                    url,
                    params=params,
                    json=data,
                    timeout=5,
                    cookies=cookies,
                    headers=headers,
                )

            if res.ok:
                r = {"host": host, "response": res.json()}
                results.append(r)
            else:
                # todo add failure to results
                logger.warning(f"Forwarding to {host} failed %s", res.text)
        except requests.exceptions.RequestException as e:
            logger.warning("Unable to connect with %s: %s", host, e)

    return results
