import csv
import json
import logging
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any
from django.contrib.auth.decorators import permission_required

from channels.db import database_sync_to_async
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_delete, post_save
from django.http import HttpResponse, JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon.audit import heartbeat, ingame_mods, online_mods, set_registered_mods
from rcon.cache_utils import ttl_cache
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig
from rconweb.settings import SECRET_KEY, TAG_VERSION

from .decorators import require_content_type
from channels.security.websocket import WebsocketDenier

from .models import DjangoAPIKey, SteamPlayer

logger = logging.getLogger("rconweb")

HTTP_AUTHORIZATION_HEADER = "HTTP_AUTHORIZATION"
AUTHORIZATION = "AUTHORIZATION"
BEARER = ("BEARER", "BEARER:")


def update_mods(sender, instance, **kwargs):
    set_registered_mods(get_moderators_accounts())


post_save.connect(update_mods, sender=User)
post_delete.connect(update_mods, sender=User)
post_save.connect(update_mods, sender=SteamPlayer)
post_delete.connect(update_mods, sender=SteamPlayer)


@database_sync_to_async
def get_user(api_key) -> User:
    user = DjangoAPIKey.objects.get(api_key=api_key)
    return user.user


@database_sync_to_async
def has_perm(scope) -> bool:
    return scope["user"].has_perm(("api.can_view_structured_logs"))


class APITokenAuthMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        ENDPOINT = "/ws/logs"
        headers = dict(scope["headers"])
        headers = {k.decode(): v.decode() for k, v in headers.items()}
        try:
            header_name, raw_api_key = headers.get("authorization", "").split(
                maxsplit=1
            )
            if not header_name.upper().strip() in BEARER:
                raw_api_key = None
        except (KeyError, ValueError):
            raw_api_key = None
            logger.info(f"Couldn't parse API key {raw_api_key=}")

        try:
            # If we don't include the salt, the hasher generates its own
            # and it will generate different hashed values every time
            hashed_api_key = make_password(raw_api_key, salt=SECRET_KEY)

            # Retrieve the user to use the normal authentication system
            # to include their permissions
            scope["user"] = await get_user(hashed_api_key)
        except DjangoAPIKey.DoesNotExist:
            scope["user"] = None
            logger.info(
                "API key not associated with a user, denying connection to %s", ENDPOINT
            )
            denier = WebsocketDenier()
            return await denier(scope, receive, send)

        if not await has_perm(scope):
            logger.warning(
                "User %s does not have permission to view %s", scope["user"], ENDPOINT
            )
            denier = WebsocketDenier()
            return await denier(scope, receive, send)

        return await self.app(scope, receive, send)


@dataclass
class RconResponse:
    result: Any = None
    command: str = None
    arguments: dict = None
    failed: bool = True
    error: str = None
    forwards_results: Any = None
    version: str | None = None

    def to_dict(self):
        # asdict() cannot convert a Django QueryDict properly
        if isinstance(self.arguments, QueryDict):
            self.arguments = self.arguments.dict()
        return asdict(self)


def api_response(*args, **kwargs):
    status_code = kwargs.pop("status_code", 200)
    return JsonResponse(RconResponse(version=TAG_VERSION, *args, **kwargs).to_dict(), status=status_code)


def api_csv_response(content, name, header):
    response = HttpResponse(
        content_type="text/csv",
    )
    response["Content-Disposition"] = 'attachment; filename="%s"' % name

    writer = csv.DictWriter(response, fieldnames=header, dialect="excel")
    writer.writerows(content)

    return response


@csrf_exempt
@require_http_methods(["POST"])
@require_content_type()
def do_login(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.debug("Login attempt without data")
        raise PermissionDenied("No data")

    name = data.get("username")
    password = data.get("password")
    try:
        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request, user)
            logger.info("Successful login: %s", name)
            return api_response(
                result=True, command="login", arguments=name, failed=False
            )
        else:
            logger.warning("Failed login attempt %s", name)
            raise PermissionDenied("Invalid login")
    except PermissionDenied:
        logger.warning("Failed login attempt %s", name)
        return api_response(command="login", arguments=name, status_code=401)


@ttl_cache(60 * 60, cache_falsy=False)
def get_moderators_accounts():
    return [(u.user.username, u.steam_id_64) for u in SteamPlayer.objects.all()]


@csrf_exempt
@require_http_methods(["GET"])
def is_logged_in(request):
    is_auth = request.user.is_authenticated
    if is_auth:
        try:
            steam_id = None
            try:
                steam_id = request.user.steamplayer.steam_id_64
            except:
                logger.warning("%s's steam id is not set ", request.user.username)
            try:
                heartbeat(request.user.username, steam_id)
            except:
                logger.exception("Unable to register mods")
        except:
            logger.exception("Can't record heartbeat")

    res = dict(authenticated=is_auth)
    return api_response(result=res, command="is_logged_in", failed=False)


@csrf_exempt
@require_http_methods(["GET"])
def do_logout(request):
    logout(request)
    return api_response(result=True, command="logout", failed=False)


def check_api_key(request):
    # Extract the header and bearer key if present, otherwise fall back on
    # requiring the user to be logged in
    try:
        header_name, raw_api_key = request.META[
            HTTP_AUTHORIZATION_HEADER
        ].split(maxsplit=1)
        if not header_name.upper().strip() in BEARER:
            raw_api_key = None
    except (KeyError, ValueError):
        raw_api_key = None

    try:
        # If we don't include the salt, the hasher generates its own
        # and it will generate different hashed values every time
        hashed_api_key = make_password(
            raw_api_key, salt=SECRET_KEY.replace("$", "")
        )
        api_key_model = DjangoAPIKey.objects.get(api_key=hashed_api_key)

        # Retrieve the user to use the normal authentication system
        # to include their permissions
        request.user = api_key_model.user
    except DjangoAPIKey.DoesNotExist:
        pass


def login_required():
    """Flag this endpoint as one that requires the user
    to be logged in.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Check if API-Key is used
            check_api_key(request)

            if not request.user.is_authenticated:
                return api_response(
                    command=request.path,
                    error="You must be logged in to use this",
                    failed=True,
                    status_code=401,
                )

            try:
                return func(request, *args, **kwargs)
            except PermissionDenied as e:
                return api_response(
                    command=request.path,
                    error="You do not have the required permissions to use this",
                    failed=True,
                    status_code=403,
                )
            except Exception as e:
                logger.exception("Unexpected error in %s", func.__name__)
                return api_response(
                    command=request.path, error=repr(e), failed=True, status_code=500
                )

        return wrapper

    return decorator


def staff_required(request):
    if request.user.is_authenticated and request.user.is_staff:
        return True
    return False


def stats_login_required(func):
    config = RconServerSettingsUserConfig.load_from_db()

    if not config.lock_stats_api:
        return func

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        check_api_key(request)


        if not request.user.is_authenticated:
            return api_response(
                command=request.path,
                error="You must be logged in to use this",
                failed=True,
                status_code=401,
            )
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.exception("Unexpected error in %s", func.__name__)
            return api_response(
                command=request.path, error=repr(e), failed=True, status_code=500
            )

    return wrapper


# TODO: Login required?
@csrf_exempt
@permission_required("api.can_view_online_admins", raise_exception=True)
@require_http_methods(["GET"])
def get_online_mods(request):
    return api_response(
        command="get_online_mods",
        result=online_mods(),
        failed=False,
    )


@csrf_exempt
@permission_required("api.can_view_ingame_admins", raise_exception=True)
@require_http_methods(["GET"])
def get_ingame_mods(request):
    return api_response(
        command="get_ingame_mods",
        result=ingame_mods(),
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def get_own_user_permissions(request):
    command_name = "get_own_user_permissions"

    permissions = Permission.objects.filter(user=request.user)
    trimmed_permissions = [
        {
            "permission": p["codename"],
            "description": p["name"],
        }
        for p in permissions.values()
    ]

    return api_response(
        command=command_name,
        result={
            "permissions": trimmed_permissions,
            "is_superuser": request.user.is_superuser,
        },
        failed=False,
    )

