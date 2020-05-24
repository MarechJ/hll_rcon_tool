import logging
import json
import datetime
from functools import wraps
from dataclasses import dataclass, asdict
from typing import Any


from rcon.audit import heartbeat, online_mods, set_registered_mods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from .models import SteamPlayer
from django.conf import settings


logger = logging.getLogger('rconweb')


@dataclass
class RconResponse:
    result: Any = None
    command: str = None
    arguments: dict = None
    failed: bool = True
    error: str = None

    def to_dict(self):
        return asdict(self)


def api_response(*args, **kwargs):
    status_code = kwargs.pop("status_code", 200)
    return JsonResponse(
        RconResponse(*args, **kwargs).to_dict(),
        status=status_code
    )


@csrf_exempt
def do_login(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise PermissionDenied("No data")

    name = data.get('username')
    password = data.get('password')
    try:
        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request, user)
            return api_response(
                result=True,
                command="login",
                arguments=name,
                failed=False
            )
        else:
            raise PermissionDenied("Invalid login")
    except PermissionDenied:
        return api_response(
            command="login",
            arguments=name,
            status_code=401
        )

@csrf_exempt
def is_logged_in(request):
    res = request.user.is_authenticated
    if res:
        try:
            heartbeat(request.user.username, request.user.steam_id_64)
            set_registered_mods([u.steam_id_64 for u in SteamPlayer.objects.all()])
        except:
            logger.warning("Can't record heartbeat")

    return api_response(
        result=res,
        command="is_logged_in",
        failed=False
    )

@csrf_exempt
def do_logout(request):
    logout(request)
    return api_response(
        result=True,
        command="logout",
        failed=False
    )


@csrf_exempt
def get_online_mods(request):
    return api_response(
        command="online_mods",
        result=online_mods(),
        failed=False,
    )


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return api_response(
                    command=request.path,
                    error="You must be logged in to use this",
                    failed=True,
                    status_code=401
                )
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return api_response(
                command=request.path,
                error=repr(e),
                failed=True,
                status_code=500
            )
    return wrapper