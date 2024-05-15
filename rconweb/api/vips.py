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
from rcon.discord import send_to_discord_audit
from rcon.models import PlayerID, PlayerVIP, enter_session
from rcon.steam_utils import is_steam_id_64
from rcon.utils import get_server_number
from rcon.win_store_utils import is_windows_store_id
from rcon.workers import get_job_results, worker_bulk_vip

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import require_content_type, require_http_methods
from .views import rcon_api

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
@require_http_methods(["POST"])
@require_content_type(["multipart/form-data"])
def upload_vips(request):
    message = "Upload a VIP file!"
    send_to_discord_audit(
        message="upload_vips", command_name="upload_vips", by=request.user.username
    )
    # Handle file upload
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            message = ""
            vips = rcon_api.get_vip_ids()
            for vip in vips:
                rcon_api.remove_vip(vip["player_id"])
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
                            rcon_api.add_vip(
                                player_id=steam_id, description=name.strip()
                            )
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
@require_http_methods(["POST"])
@require_content_type(["multipart/form-data"])
def async_upload_vips(request):
    errors = []
    send_to_discord_audit(
        message="upload_vips", command_name="upload_vips", by=request.user.username
    )
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

                    player_id, *name_chunks, possible_timestamp = line.strip().split()
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
                                f"Unable to parse {possible_timestamp=} for {name=} {player_id=}"
                            )
                            # The last chunk should be treated as part of the players name if it's not a valid date
                            name += possible_timestamp

                    if not is_steam_id_64(player_id) and not is_windows_store_id(
                        player_id
                    ):
                        errors.append(
                            f"{line} has an invalid player ID, expected a 17 digit steam id or a windows store id"
                        )
                        continue
                    if not name:
                        errors.append(
                            f"{line} doesn't have a name attached to the player ID"
                        )
                        continue
                    vips.append((name, player_id, expiration_timestamp))
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
@require_http_methods(["GET"])
def async_upload_vips_result(request):
    return api_response(
        result=get_job_results(f"upload_vip_{os.getenv('SERVER_NUMBER')}"),
        failed=False,
        command="async_upload_vips_result",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_download_vip_list", raise_exception=True)
@require_http_methods(["GET"])
def download_vips(request):
    vips = rcon_api.get_vip_ids()
    vip_lines: List[str]

    # Treating anyone without an explicit expiration date as having indefinite VIP access
    expiration_lookup: Dict[str, datetime.datetime] = defaultdict(
        lambda: datetime.datetime.utcnow() + relativedelta.relativedelta(years=200)
    )
    with enter_session() as session:
        players = (
            session.query(PlayerID)
            .join(PlayerVIP)
            .filter(PlayerVIP.server_number == get_server_number())
            .all()
        )
        for player in players:
            expiration_lookup[player.player_id] = player.vip.expiration

    vip_lines = [
        f"{vip['player_id']} {vip['name']} {expiration_lookup[vip['player_id']].isoformat()}"
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
