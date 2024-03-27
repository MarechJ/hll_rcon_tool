from logging import getLogger

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rcon.user_config.vote_map import VoteMapUserConfig
from rcon.vote_map import VoteMap

from .audit_log import record_audit
from .auth import api_response, login_required
from .decorators import require_content_type
from .user_settings import _audit_user_config_differences, _validate_user_config
from .utils import _get_data
from .views import audit

logger = getLogger(__name__)


@csrf_exempt
@login_required()
@permission_required("api.can_view_votemap_config", raise_exception=True)
@require_http_methods(["GET"])
def get_votemap_config(request):
    command_name = "get_votemap_config"

    try:
        config = VoteMapUserConfig.load_from_db()
    except Exception as e:
        logger.exception(e)
        return api_response(command=command_name, error=str(e), failed=True)

    return api_response(
        result=config.model_dump(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@require_http_methods(["GET"])
def describe_votemap_config(request):
    command_name = "describe_votemap_config"

    return api_response(
        result=VoteMapUserConfig.model_json_schema(),
        command=command_name,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_votemap_config", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def validate_votemap_config(request):
    command_name = "validate_votemap_config"
    data = _get_data(request)

    response = _validate_user_config(
        VoteMapUserConfig, data=data, command_name=command_name, dry_run=True
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_change_votemap_config", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def set_votemap_config(request):
    command_name = "set_votemap_config"
    cls = VoteMapUserConfig
    data = _get_data(request)

    response = _audit_user_config_differences(
        cls, data, command_name, request.user.username
    )

    if response:
        return response

    return api_response(
        result=True,
        command=command_name,
        arguments=data,
        failed=False,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_votemap_status", raise_exception=True)
@require_http_methods(["GET"])
def get_votemap_status(request):
    v = VoteMap()
    return api_response(
        failed=False,
        result={
            "votes": {k: str(v) for k, v in v.get_votes().items()},
            "selection": [str(m) for m in v.get_selection()],
            "results": v.get_vote_overview(),
        },
        command="set_votemap_config",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_reset_votemap_state", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def reset_votemap_state(request):
    if request.method != "POST":
        return api_response(
            failed=True,
            result="Only POST requests are supported",
            command="reset_votemap_state",
        )
    audit("reset_votemap_state", request, {})
    v = VoteMap()
    v.clear_votes()
    v.gen_selection()
    v.apply_results()
    return api_response(
        failed=False,
        result={
            "votes": v.get_votes(),
            "selection": v.get_selection(),
            "results": v.get_vote_overview(),
        },
        command="reset_votemap_state",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_map_whitelist", raise_exception=True)
@require_http_methods(["GET"])
def get_map_whitelist(request):
    v = VoteMap()
    return api_response(
        failed=False,
        result=[map for map in v.get_map_whitelist()],
        command="get_map_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_add_map_to_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_add_map_to_whitelist(request):
    data = _get_data(request)
    try:
        map_name = data["map_name"]
    except KeyError:
        return api_response(
            failed=True,
            result="map_name parameter not provided",
            command="do_add_map_to_whitelist",
        )

    v = VoteMap()
    audit("do_add_map_to_whitelist", request, {"map_name": map_name})
    v.do_add_map_to_whitelist(map_name=map_name)

    return api_response(
        failed=False,
        result=None,
        command="do_add_map_to_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_add_maps_to_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_add_maps_to_whitelist(request):
    data = _get_data(request)

    try:
        map_names = data["map_names"]
    except KeyError:
        return api_response(
            failed=True,
            result="map_name parameter not provided",
            command="do_add_maps_to_whitelist",
        )

    v = VoteMap()
    audit("do_add_maps_to_whitelist", request, {"map_names": map_names})
    v.do_add_maps_to_whitelist(map_names=map_names)

    return api_response(
        failed=False,
        result=None,
        command="do_add_maps_to_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_remove_map_from_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_remove_map_from_whitelist(request):
    data = _get_data(request)

    try:
        map_name = data["map_name"]
    except KeyError:
        return api_response(
            failed=True,
            result="map_name parameter not provided",
            command="do_remove_map_from_whitelist",
        )

    v = VoteMap()
    audit("do_remove_map_from_whitelist", request, {"map_name": map_name})
    v.do_remove_map_from_whitelist(map_name=map_name)

    return api_response(
        failed=False,
        result=None,
        command="do_remove_map_from_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_remove_maps_from_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_remove_maps_from_whitelist(request):
    data = _get_data(request)

    try:
        map_names = data["map_names"]
    except KeyError:
        return api_response(
            failed=True,
            result="map_name parameter not provided",
            command="do_remove_maps_from_whitelist",
        )

    v = VoteMap()
    audit("do_remove_maps_from_whitelist", request, {"map_names": map_names})
    v.do_remove_maps_from_whitelist(map_names=map_names)

    return api_response(
        failed=False,
        result=None,
        command="do_remove_maps_from_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_reset_map_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_reset_map_whitelist(request):
    v = VoteMap()
    audit("do_reset_map_whitelist", request, {})
    v.do_reset_map_whitelist()

    return api_response(
        failed=False,
        result=None,
        command="do_reset_map_whitelist",
    )


@csrf_exempt
@login_required()
@permission_required("api.can_set_map_whitelist", raise_exception=True)
@record_audit
@require_http_methods(["POST"])
@require_content_type()
def do_set_map_whitelist(request):
    data = _get_data(request)

    try:
        map_names = data["map_names"]
    except KeyError:
        return api_response(
            failed=True,
            result="map_name parameter not provided",
            command="do_set_map_whitelist",
        )

    v = VoteMap()
    audit("do_set_map_whitelist", request, {"map_names": map_names})
    v.do_set_map_whitelist(map_names=map_names)

    return api_response(
        failed=False,
        result=None,
        command="do_set_map_whitelist",
    )
