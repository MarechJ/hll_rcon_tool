import datetime
import logging
import os
from collections import defaultdict
from typing import Dict, List

from dateutil import parser, relativedelta
from django import forms
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rcon.commands import CommandFailedError
from rcon.discord_utils import dict_to_discord, send_to_discord_audit
from rcon.models import PlayerSteamID, PlayerVIP, enter_session
from rcon.user_config import RealVipConfig
from rcon.utils import get_server_number
from rcon.workers import get_job_results, worker_bulk_vip

from .audit_log import record_audit
from .auth import api_response, login_required
from .views import _get_data, ctl

logger = logging.getLogger("rconweb")


class DocumentForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


# TODO: should deprecate this since we use the async version
@csrf_exempt
@login_required()
@permission_required(
    {"api.can_upload_vip_list", "api.can_remove_all_vips"}, raise_exception=True
)
@record_audit
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
@login_required()
@permission_required("api.can_upload_vip_list", raise_exception=True)
@record_audit
def async_upload_vips(request):
    errors = []
    send_to_discord_audit("upload_vips", request.user.username)
    # Handle file upload
    vips = []
    if request.method == "POST":
        for name, data in request.FILES.items():
            for line in data:
                expiration_timestamp = None
                try:
                    line = line.decode()
                    if not line:
                        continue

                    steam_id, *name_chunks, possible_timestamp = line.strip().split()
                    # No possible time stamp if name_chunks is empty (only a 2 element list)
                    if not name_chunks:
                        name = possible_timestamp
                        possible_timestamp = None
                    else:
                        # This will collapse whitespace that was originally in a player's name
                        name = " ".join(name_chunks)
                        try:
                            expiration_timestamp = parser.parse(possible_timestamp)
                        except:
                            logger.warning(
                                f"Unable to parse {possible_timestamp=} for {name=} {steam_id=}"
                            )
                            # The last chunk should be treated as part of the players name if it's not a valid date
                            name += possible_timestamp

                    if len(steam_id) != 17:
                        errors.append(
                            f"{line} has an invalid steam id, expected length of 17"
                        )
                        continue
                    if not name:
                        errors.append(
                            f"{line} doesn't have a name attached to the steamid"
                        )
                        continue
                    vips.append((name, steam_id, expiration_timestamp))
                except UnicodeDecodeError:
                    errors.append("File encoding is not supported. Must use UTF8")
                    break
                except Exception as e:
                    errors.append(f"Error on line {line} {repr(2)}")
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
@login_required()
@permission_required("api.can_upload_vip_list", raise_exception=True)
def async_upload_vips_result(request):
    return api_response(
        result=get_job_results(f"upload_vip_{os.getenv('SERVER_NUMBER')}"),
        failed=False,
        command="async_upload_vips_result",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_download_vip_list", raise_exception=True)
def download_vips(request):
    vips = ctl.get_vip_ids()
    vip_lines: List[str]

    # Treating anyone without an explicit expiration date as having indefinite VIP access
    expiration_lookup: Dict[str, datetime.datetime] = defaultdict(
        lambda: datetime.datetime.utcnow() + relativedelta.relativedelta(years=200)
    )
    with enter_session() as session:
        players = (
            session.query(PlayerSteamID)
            .join(PlayerVIP)
            .filter(PlayerVIP.server_number == get_server_number())
            .all()
        )
        for player in players:
            expiration_lookup[player.steam_id_64] = player.vip.expiration

    vip_lines = [
        f"{vip['steam_id_64']} {vip['name']} {expiration_lookup[vip['steam_id_64']].isoformat()}"
        for vip in vips
    ]

    response = HttpResponse(
        "\n".join(vip_lines),
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
@login_required()
@permission_required("api.can_view_real_vip_config", raise_exception=True)
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
@login_required()
@permission_required("api.can_change_real_vip_config", raise_exception=True)
@record_audit
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
                send_to_discord_audit(
                    f"RealVIP set {dict_to_discord({k: v})}", request.user.username
                )
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
