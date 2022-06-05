import os
from functools import partial
from xmlrpc.client import Fault, ServerProxy

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rcon.discord import send_to_discord_audit

from .auth import api_response, login_required
from .utils import _get_data

supervisor_client = None

def get_supervisor_client():
    global supervisor_client

    if not supervisor_client:
        url = os.getenv('SUPERVISOR_RPC_URL')
        if not url:
            raise ValueError("Can't start services, the url of supervisor isn't set")
        supervisor_client = ServerProxy(url) 
    
    return supervisor_client


@csrf_exempt
@login_required
def get_services(request):
    info = {
        "broadcasts": "The automatic broadcasts.",
        "log_event_loop": "Blacklist enforcement, chat/kill forwarding, player history, etc...",
        "auto_settings": "Applies commands automaticaly based on your rules.",
        "cron": "The scheduler, cleans logs and whatever you added."
    }
    client = get_supervisor_client()

    processes = client.supervisor.getAllProcessInfo() 
    
    return api_response(
        result=[dict(info=info.get(p['name'], ''), **p) for p in processes],
        command="get_services",
        failed=False
    )

@csrf_exempt
@login_required
def do_service(request):
    data = _get_data(request)
    client = get_supervisor_client()
    error = None
    res = None

    actions = {
        'START': client.supervisor.startProcess,
        'STOP': client.supervisor.stopProcess
    }
    action = data.get('action')
    service_name = data.get('service_name')

    if not action or action.upper() not in actions:
        return api_response(error="action must be START or STOP", status_code=400)
    if not service_name:
        return api_response(error="process_name must be set", status_code=400)

    try:
        res = actions[action.upper()](service_name)
        send_to_discord_audit(f"do_service {service_name} {action}", request.user.username)
    except Fault as e:
        error = repr(e)

    return api_response(result=res, failed=bool(error), error=error)
