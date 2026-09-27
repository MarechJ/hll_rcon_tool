"""Manage list-scoped shares and expose their read-only partner feed."""

import json
from datetime import datetime

from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt

from rcon import vip_import, vip_sharing
from rcon.commands import HLLCommandFailedError

from .auth import api_response, login_required
from .decorators import permission_required, require_http_methods


def _body(request: HttpRequest) -> dict:
    data = json.loads(request.body)
    if not isinstance(data, dict):
        raise TypeError("Expected a JSON object")
    return data


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_shares", raise_exception=True)
@require_http_methods(["POST"])
def create_vip_list_share(request: HttpRequest):
    try:
        data = _body(request)
        expires_at = data.get("expires_at")
        if expires_at is not None:
            expires_at = datetime.fromisoformat(expires_at)
        result = vip_sharing.create_share(
            int(data["vip_list_id"]), data["name"], expires_at
        )
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        return api_response(
            command="create_vip_list_share",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    response = api_response(
        command="create_vip_list_share", result=result, failed=False
    )
    response["Cache-Control"] = "no-store"
    return response


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_shares", raise_exception=True)
@require_http_methods(["GET"])
def get_vip_list_shares(request: HttpRequest):
    try:
        result = vip_sharing.list_shares(int(request.GET["vip_list_id"]))
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            command="get_vip_list_shares", failed=True, error=str(exc), status_code=400
        )
    return api_response(command="get_vip_list_shares", result=result, failed=False)


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_shares", raise_exception=True)
@require_http_methods(["POST"])
def revoke_vip_list_share(request: HttpRequest):
    try:
        result = vip_sharing.revoke_share(
            int(_body(request)["share_id"]), revoked_by=request.user.get_username()
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            command="revoke_vip_list_share",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    return api_response(command="revoke_vip_list_share", result=result, failed=False)


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_shares", raise_exception=True)
@require_http_methods(["POST"])
def rotate_vip_list_share(request: HttpRequest):
    try:
        result = vip_sharing.rotate_share(
            int(_body(request)["share_id"]), revoked_by=request.user.get_username()
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            command="rotate_vip_list_share",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    response = api_response(
        command="rotate_vip_list_share", result=result, failed=False
    )
    response["Cache-Control"] = "no-store"
    return response


@csrf_exempt
@require_http_methods(["GET"])
def get_shared_vip_list(request: HttpRequest):
    # This credential is deliberately separate from the general CRCON API keys.
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    result = vip_sharing.get_partner_feed(token if scheme.lower() == "bearer" else "")
    if result is None:
        return api_response(
            command="get_shared_vip_list",
            failed=True,
            error="Invalid share credential",
            status_code=401,
        )
    response = api_response(command="get_shared_vip_list", result=result, failed=False)
    response["Cache-Control"] = "no-store"
    return response


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_imports", raise_exception=True)
@require_http_methods(["POST"])
def create_vip_list_import(request: HttpRequest):
    try:
        data = _body(request)
        result = vip_import.create_import(
            name=data["name"],
            source_url=data["source_url"],
            token=data["token"],
            approve_new=data.get("approve_new", True),
            servers=data.get("servers"),
            webhook_url=data.get("webhook_url"),
            retention_days=data.get("retention_days"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            command="create_vip_list_import",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    return api_response(command="create_vip_list_import", result=result, failed=False)


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_imports", raise_exception=True)
@require_http_methods(["GET"])
def get_vip_list_imports(request: HttpRequest):
    return api_response(
        command="get_vip_list_imports", result=vip_import.get_imports(), failed=False
    )


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_imports", raise_exception=True)
@require_http_methods(["POST"])
def edit_vip_list_import(request: HttpRequest):
    try:
        data = _body(request)
        result = vip_import.update_import_settings(
            int(data["vip_list_id"]),
            name=data.get("name"),
            approve_new=data["approve_new"],
            retention_days=data.get("retention_days"),
            webhook_url=data.get("webhook_url"),
            clear_webhook=data.get("clear_webhook", False),
            token=data.get("token"),
            flags=data.get("flags"),
            max_duration_seconds=data.get("max_duration_seconds"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return api_response(
            command="edit_vip_list_import", failed=True, error=str(exc), status_code=400
        )
    return api_response(command="edit_vip_list_import", result=result, failed=False)


@csrf_exempt
@login_required()
@permission_required("api.can_manage_vip_list_imports", raise_exception=True)
@require_http_methods(["POST"])
def synchronize_vip_list_import(request: HttpRequest):
    list_id = None
    try:
        list_id = int(_body(request)["vip_list_id"])
        result = vip_import.sync_import(list_id)
    except (KeyError, TypeError, ValueError) as exc:
        if list_id is not None:
            vip_import.notify_import_error(list_id)
        return api_response(
            command="synchronize_vip_list_import",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    return api_response(
        command="synchronize_vip_list_import", result=result, failed=False
    )


@csrf_exempt
@login_required()
@permission_required("api.can_approve_vip_list_imports", raise_exception=True)
@require_http_methods(["POST"])
def set_vip_list_import_record_policy(request: HttpRequest):
    try:
        data = _body(request)
        result = vip_import.set_import_record_policy(
            int(data["record_id"]),
            approved=data.get("approved"),
            excluded=data.get("excluded"),
        )
    except (KeyError, TypeError, ValueError, HLLCommandFailedError) as exc:
        return api_response(
            command="set_vip_list_import_record_policy",
            failed=True,
            error=str(exc),
            status_code=400,
        )
    return api_response(
        command="set_vip_list_import_record_policy", result=result, failed=False
    )
