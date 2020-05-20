import logging
import json
import datetime
from functools import wraps
from dataclasses import dataclass, asdict
from typing import Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import PermissionDenied
from django.contrib.auth import authenticate, login, logout

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
            return JsonResponse({
                "result": {},
                "command": "login",
                "arguments": name,
                "failed": False
            })
        else:
            raise PermissionDenied("Invalid login")
    except PermissionDenied:
        return JsonResponse({
                "result": {},
                "command": "login",
                "arguments": name,
                "failed": True
        })

@csrf_exempt
def is_logged_in(request):
    return JsonResponse({
        "result": request.user.is_authenticated,
        "command": "is_logged_in",
        "arguments": None,
        "failed": request.user.is_authenticated
    })

@csrf_exempt
def do_logout(request):
    logout(request)
    return JsonResponse({
        "result": True,
        "command": "logout",
        "arguments": None,
        "failed": False
    })


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