import logging
import json
import datetime


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth import PermissionDenied
from django.contrib.auth import authenticate, login, logout

logger = logging.getLogger('rconweb')

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
