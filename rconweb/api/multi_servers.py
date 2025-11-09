import json
import logging
import os
from copy import deepcopy
from typing import Any

import requests
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from rcon.api_commands import RconAPI
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rcon.utils import ApiKey, get_server_number

from .auth import AUTHORIZATION, api_response, login_required
from .decorators import permission_required, require_http_methods
from .models import UserServerPermission

logger = logging.getLogger("rcon")


def _get_allowed_server_numbers(user):
    if user.is_superuser:
        return None

    user_permissions = UserServerPermission.objects.filter(user=user)
    if user_permissions.exists():
        # User has specific server permissions - restrict to those servers only
        return set(perm.server_number for perm in user_permissions)
    else:
        # User has no permission records - can view all servers (backward compatible)
        return None


@login_required()
@csrf_exempt
@require_http_methods(["GET"])
def get_server_list(request):
    """
    Get list of servers the user has permission to access.

    Query Parameters:
        include_current (str): 'true' to include the current server in the list.
                              Default: 'false' (backward compatible)

    Response with include_current=false (default):
        {
            "result": [
                {"name": "Server 2", "port": "8020", "server_number": 2},
                {"name": "Server 3", "port": "8030", "server_number": 3}
            ],
            "command": "server_list",
            "failed": false
        }

    Response with include_current=true:
        {
            "result": [
                {"name": "Server 1", "port": "8010", "server_number": 1, "current": true},
                {"name": "Server 2", "port": "8020", "server_number": 2, "current": false},
                {"name": "Server 3", "port": "8030", "server_number": 3, "current": false}
            ],
            "command": "server_list",
            "failed": false
        }
    """
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

    # Add current server if requested
    if include_current:
        try:
            from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
            from rcon.utils import get_server_number

            config = RconServerSettingsUserConfig.load_from_db()
            current_server_number = int(get_server_number())

            # Check if user has permission to view current server
            if allowed_server_numbers is None or current_server_number in allowed_server_numbers:
                current_server = {
                    "name": config.short_name,
                    "port": os.getenv("RCONWEB_PORT"),
                    "link": str(config.server_url) if config.server_url else None,
                    "server_number": current_server_number,
                    "current": True,
                }
                server_list.append(current_server)
                logger.debug(
                    f"Added current server {current_server_number} to list for user {request.user.username}"
                )
            else:
                logger.debug(
                    f"User {request.user.username} does not have permission to view "
                    f"current server {current_server_number}"
                )
        except Exception as e:
            logger.error(f"Failed to get current server info: {e}")

    # Add other servers
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

            # Get server_number from response
            server_number = info["result"].get("server_number")

            # Check if user has permission to view this server
            if allowed_server_numbers is not None and server_number not in allowed_server_numbers:
                logger.debug(
                    f"User {request.user.username} does not have permission to view "
                    f"server {server_number}"
                )
                continue

            # Add 'current' flag if include_current is enabled
            if include_current:
                info["result"]["current"] = False

            server_list.append(info["result"])
        except Exception as e:
            logger.warning("Unable to connect with %s: %s", host, e)

    logger.info(
        f"Returning {len(server_list)} server(s) for user {request.user.username} "
        f"(include_current={include_current})"
    )

    return api_response(server_list, failed=False, command="server_list")


def forward_request(request):
    """
    Forward request to other servers.
    Only forwards to servers the user has permission to access.
    """
    # Get user's allowed servers
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
            # First, get server info to check permissions
            info_url = f"http://{host}/api/get_connection_info"
            info_res = requests.get(
                info_url,
                timeout=5,
                cookies=cookies,
                headers=headers,
            )

            if not info_res.ok:
                logger.warning(f"Unable to get server info from {host}")
                continue

            server_number = info_res.json()["result"].get("server_number")

            # Check if user has permission to forward to this server
            if allowed_server_numbers is not None and server_number not in allowed_server_numbers:
                logger.debug(
                    f"User {request.user.username} does not have permission to forward to server {server_number}"
                )
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
    user=None,
):
    """
    Forward command to other servers.
    Only forwards to servers the user has permission to access.
    """
    # Get user's allowed servers if user is provided
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
            # Check permissions if user is provided
            if user and allowed_server_numbers is not None:
                # Get server info to check permissions
                info_url = f"http://{host}/api/get_connection_info"
                info_res = requests.get(
                    info_url,
                    timeout=5,
                    cookies=cookies,
                    headers=headers,
                )

                if not info_res.ok:
                    logger.warning(f"Unable to get server info from {host}")
                    continue

                server_number = info_res.json()["result"].get("server_number")

                # Check if user has permission to forward to this server
                if server_number not in allowed_server_numbers:
                    logger.debug(
                        f"User {user.username} does not have permission to forward to server {server_number}"
                    )
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
