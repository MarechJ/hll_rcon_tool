import json
import logging
from copy import deepcopy
from typing import Any

import requests
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import ApiKey

from .auth import AUTHORIZATION, api_response, login_required
from .decorators import permission_required, require_http_methods
from .models import UserServerPermission

logger = logging.getLogger("rcon")


def _get_allowed_server_numbers(user):
    """
    Get set of server numbers the user has permission to access.
    Returns None if user can access all servers.
    """
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
    Get list of other servers (excluding current server).
    Legacy endpoint - kept for backward compatibility.

    If user has UserServerPermission records, only return those servers.
    If user has no UserServerPermission records, return all servers (backward compatible).
    Superusers always see all servers.
    """
    allowed_server_numbers = _get_allowed_server_numbers(request.user)

    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    auth_header: str | None = request.headers.get(AUTHORIZATION)
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}

    logger.debug(keys)
    names = []

    # Add other servers (excluding current)
    for host, key in keys.items():
        if key == my_key:
            continue
        url = f"http://{host}/api/get_connection_info"
        try:
            res = requests.get(
                url,
                timeout=5,
                cookies=dict(sessionid=request.COOKIES.get("sessionid")),
                headers=headers,
            )
            if res.ok:
                server_info = res.json()["result"]
                server_number = server_info.get("server_number")

                # Filter servers based on user permissions
                if allowed_server_numbers is None or server_number in allowed_server_numbers:
                    names.append(server_info)
                else:
                    logger.debug(
                        f"User {request.user.username} does not have permission to view server {server_number}"
                    )
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {url}")

    return api_response(names, failed=False, command="server_list")


@login_required()
@csrf_exempt
@require_http_methods(["GET"])
def get_user_servers(request):
    """
    Get complete list of all servers the user has permission to access, including the current server.

    Returns a list with a 'current' flag to identify which server the user is currently on.
    This is more efficient than get_server_list as it requires only one request.

    If user has UserServerPermission records, only return those servers.
    If user has no UserServerPermission records, return all servers (backward compatible).
    Superusers always see all servers.
    """
    import os
    from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
    from rcon.utils import get_server_number
    from rcon.api_commands import RconAPI

    allowed_server_numbers = _get_allowed_server_numbers(request.user)

    api_key = ApiKey()
    keys = api_key.get_all_keys()
    my_key = api_key.get_key()

    auth_header: str | None = request.headers.get(AUTHORIZATION)
    headers = {"AUTHORIZATION": auth_header} if auth_header else {}

    logger.debug(keys)
    servers = []

    # Add current server to the list
    try:
        config = RconServerSettingsUserConfig.load_from_db()
        rcon_api = RconAPI()
        current_server_number = int(get_server_number())

        # Check if user has permission to view current server
        if allowed_server_numbers is None or current_server_number in allowed_server_numbers:
            current_server_info = {
                "name": rcon_api.get_name(),
                "port": os.getenv("RCONWEB_PORT"),
                "link": str(config.server_url) if config.server_url else config.server_url,
                "server_number": current_server_number,
                "current": True,
            }
            servers.append(current_server_info)
    except Exception as e:
        logger.error(f"Failed to get current server info: {e}")

    # Add other servers
    for host, key in keys.items():
        if key == my_key:
            continue
        url = f"http://{host}/api/get_connection_info"
        try:
            res = requests.get(
                url,
                timeout=5,
                cookies=dict(sessionid=request.COOKIES.get("sessionid")),
                headers=headers,
            )
            if res.ok:
                server_info = res.json()["result"]
                server_number = server_info.get("server_number")

                # Filter servers based on user permissions
                if allowed_server_numbers is None or server_number in allowed_server_numbers:
                    server_info["current"] = False
                    servers.append(server_info)
                else:
                    logger.debug(
                        f"User {request.user.username} does not have permission to view server {server_number}"
                    )
        except requests.exceptions.RequestException:
            logger.warning(f"Unable to connect with {url}")

    return api_response(servers, failed=False, command="get_user_servers")


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
