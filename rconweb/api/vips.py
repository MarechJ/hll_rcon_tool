import csv
import datetime
import io
import logging
import os
from datetime import UTC

from dateutil import parser
from django import forms
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rcon.commands import HLLCommandFailedError
from rcon.discord import send_to_discord_audit
from rcon.steam_utils import is_steam_id_64
from rcon.utils import INDEFINITE_VIP_DATE
from rcon.win_store_utils import is_windows_store_id
from rcon.workers import get_job_results, worker_bulk_vip

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import permission_required, require_content_type, require_http_methods
from .views import rcon_api

logger = logging.getLogger("rconweb")


class DocumentForm(forms.Form):
    docfile = forms.FileField(label="Select a file")


@csrf_exempt
@login_required()
@permission_required("api.can_upload_vip_list", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type(["multipart/form-data"])
def upload_vips(request):
    errors = []
    send_to_discord_audit(
        message="upload_vips", command_name="upload_vips", by=request.user.username
    )
    # Handle file upload
    vips = []
    if request.method == "POST":
        for name, data in request.FILES.items():
            for idx, line in enumerate(data):
                idx += 1
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
                        except:  # noqa
                            logger.warning(
                                f"#{idx} Unable to parse {possible_timestamp=} for {name=} {player_id=}"
                            )
                            # The last chunk should be treated as part of the players name if it's not a valid date
                            name += possible_timestamp

                    if not is_steam_id_64(player_id) and not is_windows_store_id(
                        player_id
                    ):
                        errors.append(
                            f"#{idx} {line} has an invalid player ID: `{player_id}`, expected a 17 digit steam id or a windows store id. {is_steam_id_64(player_id)=} {is_windows_store_id(player_id)=}"
                        )
                        continue
                    if not name:
                        errors.append(
                            f"#{idx}  {line} doesn't have a name attached to the player ID"
                        )
                        continue
                    vips.append((name, player_id, expiration_timestamp))
                except UnicodeDecodeError:
                    errors.append("File encoding is not supported. Must use UTF8")
                    break
                except Exception as e:  # noqa
                    errors.append(f"#{idx} Error on line {line}: {e}")
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
        command="upload_vips",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_upload_vip_list", raise_exception=True)
@require_http_methods(["GET"])
def upload_vips_result(request):
    return api_response(
        result=get_job_results(f"upload_vip_{os.getenv('SERVER_NUMBER')}"),
        failed=False,
        command="upload_vips_result",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_download_vip_list", raise_exception=True)
@require_http_methods(["GET"])
def download_vips(request):
    vips = rcon_api.get_vip_ids()

    # Preserve the legacy text format while sourcing expiration timestamps
    # from the effective VIP Lists state returned by get_vip_ids().
    vip_lines = [
        (
            f"{vip['player_id']} {vip['name']} "
            f"{(vip['vip_expiration'] or INDEFINITE_VIP_DATE).isoformat()}"
        )
        for vip in vips
    ]

    response = HttpResponse(
        "\n".join(vip_lines),
        content_type="text/plain",
    )

    response["Content-Disposition"] = (
        f"attachment; filename={datetime.datetime.now(tz=UTC).isoformat()}_vips.txt"
    )
    return response


def _parse_vip_list_import(content: str) -> list[dict]:
    """Parse a VIP list import from CSV or the legacy text format."""
    content = content.lstrip("\ufeff").strip()
    if not content:
        return []

    first_line = content.splitlines()[0]
    if "player_id" in first_line and "," in first_line:
        return _parse_vip_list_csv_import(content)

    return _parse_vip_list_legacy_import(content)


def _parse_vip_list_csv_import(content: str) -> list[dict]:
    """Parse the CSV format produced by the VIP list export."""
    reader = csv.DictReader(io.StringIO(content))

    if reader.fieldnames is None or "player_id" not in reader.fieldnames:
        raise ValueError("VIP list CSV must contain a player_id column")

    has_expires_at = "expires_at" in reader.fieldnames
    entries = []

    for line_number, row in enumerate(reader, start=2):
        player_id = (row.get("player_id") or "").strip()
        if not player_id:
            raise ValueError(f"Missing player_id in VIP list CSV line {line_number}")

        entry = {
            "player_id": player_id,
            "steam_id": (row.get("steam_id") or "").strip() or None,
            "description": (
                (row.get("description") or "").strip()
                or (row.get("player_name") or "").strip()
                or None
            ),
            "notes": (row.get("notes") or "").strip() or None,
        }

        if has_expires_at:
            expires_at = (row.get("expires_at") or "").strip()
            entry["expires_at"] = (
                datetime.datetime.fromisoformat(expires_at) if expires_at else None
            )

        entries.append(entry)

    return entries


def _parse_vip_list_legacy_import(content: str) -> list[dict]:
    """Parse the legacy CRCON VIP text format."""
    entries = []

    for line_number, line in enumerate(content.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if not parts:
            continue

        player_id = parts[0]
        description = None
        expires_at = None

        if len(parts) > 1:
            try:
                parsed_expiration = datetime.datetime.fromisoformat(parts[-1])
            except ValueError:
                description_parts = parts[1:]
            else:
                description_parts = parts[1:-1]
                if parsed_expiration.year >= 3000:
                    expires_at = None
                else:
                    expires_at = parsed_expiration

            description = " ".join(description_parts).strip() or None

        entries.append(
            {
                "player_id": player_id,
                "description": description,
                "expires_at": expires_at,
                "notes": None,
            }
        )

    return entries


VIP_LIST_EXPORT_FIELDS = (
    "list_id",
    "list_name",
    "record_id",
    "player_id",
    "steam_id",
    "player_name",
    "active",
    "expired",
    "expires_at",
    "description",
    "notes",
    "admin_name",
    "created_at",
)


def _vip_list_export_response(records, lists, filename):
    list_names = {vip_list["id"]: vip_list["name"] for vip_list in lists}

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=VIP_LIST_EXPORT_FIELDS,
        lineterminator="\n",
    )
    writer.writeheader()

    for record in records:
        writer.writerow(
            {
                "list_id": record["vip_list_id"],
                "list_name": list_names.get(record["vip_list_id"], ""),
                "record_id": record["id"],
                "player_id": record["player_id"],
                "steam_id": record.get("steam_id") or "",
                "player_name": record["player_name"] or "",
                "active": record["is_active"],
                "expired": record["is_expired"],
                "expires_at": (
                    record["expires_at"].isoformat()
                    if record["expires_at"] is not None
                    else ""
                ),
                "description": record["description"] or "",
                "notes": record["notes"] or "",
                "admin_name": record["admin_name"],
                "created_at": record["created_at"].isoformat(),
            }
        )

    response = HttpResponse(
        output.getvalue(),
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
@login_required()
@permission_required("api.can_change_vip_list_records", raise_exception=True)
@require_http_methods(["POST"])
@require_content_type(["multipart/form-data"])
def preview_vip_list_import_file(request):
    try:
        vip_list_id = int(request.POST["vip_list_id"])
    except (KeyError, TypeError, ValueError):
        return api_response(
            error="A valid vip_list_id is required",
            failed=True,
            status_code=400,
        )

    mode = request.POST.get("mode", "merge")

    if not request.FILES:
        return api_response(
            error="A VIP list import file is required",
            failed=True,
            status_code=400,
        )

    if len(request.FILES) != 1:
        return api_response(
            error="Exactly one VIP list import file is required",
            failed=True,
            status_code=400,
        )

    uploaded_file = next(iter(request.FILES.values()))

    try:
        content = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return api_response(
            error="File encoding is not supported. Must use UTF8",
            failed=True,
            status_code=400,
        )

    try:
        entries = _parse_vip_list_import(content)
        preview = rcon_api.preview_vip_list_import(
            vip_list_id=vip_list_id,
            entries=entries,
            mode=mode,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            error=str(exc),
            failed=True,
            status_code=400,
        )

    return api_response(
        result=preview,
        failed=False,
        command="preview_vip_list_import_file",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_vip_list_records", raise_exception=True)
@require_http_methods(["POST"])
@require_content_type(["multipart/form-data"])
def import_vip_list_file(request):
    try:
        vip_list_id = int(request.POST["vip_list_id"])
    except (KeyError, TypeError, ValueError):
        return api_response(
            error="A valid vip_list_id is required",
            failed=True,
            status_code=400,
        )

    mode = request.POST.get("mode", "merge")

    if not request.FILES:
        return api_response(
            error="A VIP list import file is required",
            failed=True,
            status_code=400,
        )

    if len(request.FILES) != 1:
        return api_response(
            error="Exactly one VIP list import file is required",
            failed=True,
            status_code=400,
        )

    uploaded_file = next(iter(request.FILES.values()))

    try:
        content = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return api_response(
            error="File encoding is not supported. Must use UTF8",
            failed=True,
            status_code=400,
        )

    try:
        entries = _parse_vip_list_import(content)
        result = rcon_api.import_vip_list_records(
            vip_list_id=vip_list_id,
            entries=entries,
            mode=mode,
            admin_name=request.user.username,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            error=str(exc),
            failed=True,
            status_code=400,
        )

    return api_response(
        result=result,
        failed=False,
        command="import_vip_list_file",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_vip_lists", raise_exception=True)
@require_http_methods(["GET"])
def download_vip_list(request):
    try:
        vip_list_id = int(request.GET["vip_list_id"])
    except (KeyError, TypeError, ValueError):
        return api_response(
            error="A valid vip_list_id is required",
            status_code=400,
        )

    try:
        vip_list = rcon_api.get_vip_list(vip_list_id)
    except HLLCommandFailedError as exc:
        logger.warning(
            "Unable to export VIP list ID %s: %s",
            vip_list_id,
            exc,
        )
        return api_response(
            error="VIP list not found",
            status_code=404,
        )

    records = rcon_api.get_vip_list_records(vip_list_id)

    timestamp = datetime.datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")

    return _vip_list_export_response(
        records,
        [vip_list],
        f"{timestamp}_vip_list_{vip_list_id}.csv",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_vip_lists", raise_exception=True)
@require_http_methods(["GET"])
def download_all_vip_lists(request):
    lists = rcon_api.get_vip_lists()
    records = rcon_api.get_all_vip_records()

    timestamp = datetime.datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")

    return _vip_list_export_response(
        records,
        lists,
        f"{timestamp}_vip_lists_all.csv",
    )
