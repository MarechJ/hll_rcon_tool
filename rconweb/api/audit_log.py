import json
import logging
from functools import wraps

from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import and_, or_

from rcon.models import AuditLog, enter_session

from .auth import api_response, login_required
from .decorators import require_http_methods
from .utils import _get_data

logger = logging.getLogger("rconweb")


def _to_list(value):
    if not isinstance(value, list):
        return [value]
    return value


def record_audit(func):
    @wraps(func)
    def wrapper(request, **kwargs):
        name = request.path.split("/")[-1]
        data = _get_data(request)
        user = request.user.username

        try:
            raw = func(request, **kwargs)
            result = raw.content.decode()
        except Exception as e:
            result = repr(e)
            raise
        finally:
            with enter_session() as sess:
                sess.add(
                    AuditLog(
                        username=user,
                        command=name,
                        command_arguments=json.dumps(data),
                        command_result=result,
                    )
                )

        return raw

    return wrapper


def auto_record_audit(name):
    def wrapper(func):
        # A few get_ methods can be called w/ POST but don't modify anything
        # so filtering like this should work since this is only for the RconAPI exposed
        # endpoints, manually defined endpoints use the @record_audit endpoint
        if not name.startswith("get_") and not name.startswith("validate_"):
            return record_audit(func)
        else:
            return func

    return wrapper


@csrf_exempt
@login_required()
@permission_required("api.can_view_audit_logs_autocomplete", raise_exception=True)
@require_http_methods(["GET"])
def get_audit_logs_autocomplete(request):
    failed = False
    error = None
    res = None
    try:
        with enter_session() as sess:
            usernames = [u for u, in sess.query(AuditLog.username).distinct().all()]
            commands = [c for c, in sess.query(AuditLog.command).distinct().all()]
            logger.debug("Audit metadata: %s %s", usernames, commands)
    except Exception as e:
        logger.exception("Getting audit log failed")
        failed = True
        error = e

    return api_response(
        result={"usernames": usernames, "commands": commands},
        command="get_audit_logs_autocomplete",
        arguments=None,
        failed=failed,
        error=error,
    )


@csrf_exempt
@login_required()
@permission_required("api.can_view_audit_logs", raise_exception=True)
@require_http_methods(["GET"])
def get_audit_logs(request):
    data = _get_data(request)
    and_conditions = []
    failed = False
    error = None

    try:
        with enter_session() as sess:
            query = sess.query(AuditLog)

            if usernames := data.get("usernames"):
                usernames = _to_list(usernames)
                and_conditions.append(AuditLog.username.in_(usernames))
            if commands := data.get("commands"):
                commands = _to_list(commands)
                and_conditions.append(AuditLog.command.in_(commands))
            if parameters := data.get("parameters"):
                parameters = _to_list(parameters)
                conditions = [
                    AuditLog.command_arguments.ilike(f"%{c}%") for c in parameters
                ]
                if len(conditions) == 1:
                    and_conditions.append(conditions[0])
                else:
                    and_conditions.append(or_(*conditions))

            if and_conditions:
                logger.debug("condition %s", and_conditions)
                if len(and_conditions) > 1:
                    and_conditions = and_(*and_conditions)
                else:
                    and_conditions = and_conditions[0]
                query = query.filter(and_conditions)
                logger.debug(query)

            if data.get("time_sort") == "asc":
                query = query.order_by(AuditLog.creation_time.asc())
            else:
                query = query.order_by(AuditLog.creation_time.desc())

            res = query.all()
            res = [r.to_dict() for r in res]
    except Exception as e:
        logger.exception("Getting audit log failed")
        failed = True
        error = e

    return api_response(
        result=res, command="get_audit_logs", arguments=None, failed=failed, error=error
    )
