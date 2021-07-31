import datetime
from re import escape
from django.forms.utils import ErrorList

from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django import forms
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import MapsHistory
from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.steam_utils import get_steam_profile
from rcon.settings import SERVER_INFO
from rcon import game_logs
from rcon.models import LogLine, PlayerSteamID, PlayerName, enter_session
from rcon.discord import dict_to_discord, send_to_discord_audit
from rcon.workers import worker_bulk_vip, get_job_results
from .auth import login_required, api_response
from .views import ctl
from .views import _get_data
import os
from rcon.user_config import RealVipConfig
import logging

logger = logging.getLogger("rconweb")

class DocumentForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


@csrf_exempt
@login_required
def upload_vips(request):
    message = "Upload a VIP file!"
    send_to_discord_audit("upload_vips", request.user.username)
    # Handle file upload
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            message = ""
            vips = ctl.get_vip_ids()
            for vip in vips:
                ctl.do_remove_vip(vip["steam_id_64"])
            message = f"{len(vips)} removed\n"
            count = 0
            for name, data in request.FILES.items():
                if name.endswith(".json"):
                    message = "JSON is not handled yet"
                    break
                else:
                    for l in data:
                        try:
                            l = l.decode()
                            steam_id, name = l.split(" ", 1)
                            if len(steam_id) != 17:
                                raise ValueError
                            ctl.do_add_vip(name.strip(), steam_id)
                            count += 1
                        except UnicodeDecodeError:
                            message = "File encoding is not supported. Must use UTF8"
                            break
                        except ValueError:
                            message += f"Line: '{l}' is invalid, skipped\n"
                        except CommandFailedError:
                            message = "The game serveur returned an error while adding a VIP. You need to upload again"
                            break

                    message += f"{count} added"
        else:
            message = "The form is not valid. Fix the following error:"
    else:
        form = DocumentForm()  # An empty, unbound form

    # Render list page with the documents and the form
    context = {"form": form, "message": message}
    return render(request, "list.html", context)


@csrf_exempt
@login_required
def async_upload_vips(request):
    errors = []
    send_to_discord_audit("upload_vips", request.user.username)
    # Handle file upload
    vips = []
    if request.method == "POST":
        for name, data in request.FILES.items():
            for l in data:
                try:
                    l = l.decode()
                    if not l:
                        continue
                    steam_id, name = l.split(" ", 1)
                    if len(steam_id) != 17:
                        errors.append(
                            f"{l} has an invalid steam id, expecter length of 17"
                        )
                        continue
                    if not name:
                        errors.append(
                            f"{l} doesn't have a name attached to the steamid"
                        )
                        continue
                    vips.append((name, steam_id))
                except UnicodeDecodeError:
                    errors.append("File encoding is not supported. Must use UTF8")
                    break
    else:
        return api_response(error="Bad method", status_code=400)

    if vips:
        worker_bulk_vip(
            vips, job_key=f"upload_vip_{os.getenv('SERVER_NUMBER')}", mode="override"
        )
    else:
        errors.append("No vips submitted")

    # Render list page with the documents and the form
    return api_response(
        result="Job submitted, will take several minutes",
        failed=bool(errors),
        error="\n".join(errors),
        command="async_upload_vips",
    )


@csrf_exempt
@login_required
def async_upload_vips_result(request):
    return api_response(
        result=get_job_results(f"upload_vip_{os.getenv('SERVER_NUMBER')}"),
        failed=False,
        command="async_upload_vips_result",
    )


@csrf_exempt
@login_required
def download_vips(request):
    vips = ctl.get_vip_ids()
    response = HttpResponse(
        "\n".join([f"{vip['steam_id_64']} {vip['name']}" for vip in vips]),
        content_type="text/plain",
    )
    response[
        "Content-Disposition"
    ] = f"attachment; filename={datetime.datetime.now().isoformat()}_vips.txt"
    return response


def _get_real_vip_config():
    config = RealVipConfig()
    return {
        "enabled": config.get_enabled(),
        "desired_total_number_vips": config.get_desired_total_number_vips(),
        "minimum_number_vip_slot": config.get_minimum_number_vip_slot(),
    }


@csrf_exempt
@login_required
def get_real_vip_config(request):
    error = None
    try:
        real_vip_config = _get_real_vip_config()
    except Exception as e:
        error = repr(e)
    return api_response(
        result=real_vip_config,
        failed=bool(error),
        error=error,
        command="get_real_vip_config",
    )


@csrf_exempt
@login_required
def set_real_vip_config(request):
    error = None
    data = _get_data(request)
    try:
        config = RealVipConfig()
        real_vip_config = {
            "enabled": (bool, config.set_enabled),
            "desired_total_number_vips": (int, config.set_desired_total_number_vips),
            "minimum_number_vip_slot": (int, config.set_minimum_number_vip_slot),
        }
        for k, v in data.items():
            if k in real_vip_config:
                cast, setter = real_vip_config[k]
                send_to_discord_audit(f"RealVIP set {dict_to_discord({k: v})}", request.user.username)
                setter(cast(v))
    except Exception as e:
        logger.exception("Failed to set realvip config")
        error = repr(e)
    return api_response(
        result=_get_real_vip_config(),
        failed=bool(error),
        error=error,
        command="get_real_vip_config",
    )