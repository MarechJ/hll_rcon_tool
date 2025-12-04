import json
import logging
import os
from copy import deepcopy
from typing import Any

import requests
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import ApiKey, get_server_number

from .auth import AUTHORIZATION, api_response, login_required
from .decorators import require_http_methods
from .models import UserServerPermission

logger = logging.getLogger("rcon")


def _get_allowed_server_numbers(user):
    if user.is_superuser:
        return None

    user_permissions = UserServerPermission.objects.filter(user=user)
    if user_permissions.exists():
        return set(perm.server_number for perm in user_permissions)
    else:
        return None


@csrf_exempt
@require_http_methods(["GET"])
def get_accessible_servers(request):
    if not request.user.is_authenticated:
        return api_response(
            command="get_accessible_servers",
            error="You must be logged in to use this",
            failed=True,
            status_code=401,
        )

    allowed_server_numbers = _get_allowed_server_numbers(request.user)

    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    sessionid: str | None = request.COOKIES.get("sessionid")
    auth_header: str | None = request.headers.get(AUTHORIZATION)
    cookies = {"sessionid": sessionid} if sessionid else {}
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}

    server_list = []

    try:
        config = RconServerSettingsUserConfig.load_from_db()
        current_server_number = int(get_server_number())

        if allowed_server_numbers is None or current_server_number in allowed_server_numbers:
            current_server = {
                "name": config.short_name,
                "port": os.getenv("RCONWEB_PORT"),
                "link": str(config.server_url) if config.server_url else None,
                "server_number": current_server_number,
            }
            server_list.append(current_server)
    except Exception as e:
        logger.error("Failed to get current server info: %s", e)

    for host, key in keys.items():
        if key == my_key:
            continue

        try:
            info_res = requests.get(
                f"http://{host}/api/get_connection_info",
                cookies=cookies,
                headers=headers,
                timeout=2,
            )
            info = info_res.json()

            server_number = info["result"].get("server_number")

            if allowed_server_numbers is not None and server_number not in allowed_server_numbers:
                continue

            server_list.append(info["result"])
        except Exception as e:
            logger.warning("Unable to connect with %s: %s", host, e)

    return api_response(server_list, failed=False, command="get_accessible_servers")


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def get_server_list(request):
    allowed_server_numbers = _get_allowed_server_numbers(request.user)
    include_current = request.GET.get('include_current', 'false').lower() == 'true'

    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    sessionid: str | None = request.COOKIES.get("sessionid")
    auth_header: str | None = request.headers.get(AUTHORIZATION)
    cookies = {"sessionid": sessionid} if sessionid else {}
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}
    server_list = []

    if include_current:
        try:
            config = RconServerSettingsUserConfig.load_from_db()
            current_server_number = int(get_server_number())

            if allowed_server_numbers is None or current_server_number in allowed_server_numbers:
                current_server = {
                    "name": config.short_name,
                    "port": os.getenv("RCONWEB_PORT"),
                    "link": str(config.server_url) if config.server_url else None,
                    "server_number": current_server_number,
                    "current": True,
                }
                server_list.append(current_server)
        except Exception as e:
            logger.error("Failed to get current server info: %s", e)

    for host, key in keys.items():
        if key == my_key:
            continue

        try:
            info_res = requests.get(
                f"http://{host}/api/get_connection_info",
                cookies=cookies,
                headers=headers,
                timeout=2,
            )
            info = info_res.json()

            server_number = info["result"].get("server_number")

            if allowed_server_numbers is not None and server_number not in allowed_server_numbers:
                continue

            if include_current:
                info["result"]["current"] = False

            server_list.append(info["result"])
        except Exception as e:
            logger.warning("Unable to connect with %s: %s", host, e)

    return api_response(server_list, failed=False, command="server_list")


def forward_request(request):
    allowed_server_numbers = _get_allowed_server_numbers(request.user)

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
            info_url = f"http://{host}/api/get_connection_info"
            info_res = requests.get(
                info_url,
                timeout=5,
                cookies=cookies,
                headers=headers,
            )

            if not info_res.ok:
                logger.warning("Unable to get server info from %s", host)
                continue

            server_number = info_res.json()["result"].get("server_number")

            if allowed_server_numbers is not None and server_number not in allowed_server_numbers:
                continue

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
                logger.warning("Forwarding to %s failed %s", host, res.text)
        except requests.exceptions.RequestException:
            logger.warning("Unable to connect with %s", url)

    return results


def forward_command(
    path: str,
    sessionid: str | None,
    auth_header: str | None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | QueryDict | None = None,
    user=None,
):
    allowed_server_numbers = _get_allowed_server_numbers(user) if user else None

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
            if user and allowed_server_numbers is not None:
                info_url = f"http://{host}/api/get_connection_info"
                info_res = requests.get(
                    info_url,
                    timeout=5,
                    cookies=cookies,
                    headers=headers,
                )

                if not info_res.ok:
                    logger.warning("Unable to get server info from %s", host)
                    continue

                server_number = info_res.json()["result"].get("server_number")

                if server_number not in allowed_server_numbers:
                    continue

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
                logger.warning("Forwarding to %s failed %s", host, res.text)
        except requests.exceptions.RequestException as e:
            logger.warning("Unable to connect with %s: %s", host, e)

    return results
