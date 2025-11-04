import logging
import os
from functools import wraps

from django.contrib.auth.decorators import (
    permission_required as django_permission_required,
)
from django.http import JsonResponse
from django.views.decorators.http import (
    require_http_methods as django_require_http_methods,
)

logger = logging.getLogger("rconweb")

ENDPOINT_HTTP_METHODS: dict[str, list[str]] = {}
ENDPOINT_PERMISSIONS_LOOKUP = {}


def permission_required(
    perm: str | list[str] | set[str], login_url=None, raise_exception=False
):
    def decorator(
        func,
    ):
        if isinstance(perm, str):
            ENDPOINT_PERMISSIONS_LOOKUP[func.__name__] = [perm]
        else:
            ENDPOINT_PERMISSIONS_LOOKUP[func.__name__] = perm

        @wraps(func)
        @django_permission_required(
            perm, login_url=login_url, raise_exception=raise_exception
        )
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return decorator


def require_http_methods(request_method_list: list[str]):
    def decorator(
        func,
    ):
        if func.__name__ in ENDPOINT_HTTP_METHODS:
            # TODO: I have only seen this error when launching 4+ game servers within the same install
            # I haven't done any looking to figure out why it happens, it should be unique to each Python
            # interpreter instance, maybe some sort of weird race condition and I think there is likely
            # a better underlying fix we can make, but this will resolve issues immediately for users
            # and I don't think it will hurt anything, worst case there's some extraneous log statements
            logger.error(f"{func.__name__} already added to ENDPOINT_HTTP_METHODS")
            return
            # raise ValueError(f"{func.__name__} already added to ENDPOINT_HTTP_METHODS")

        ENDPOINT_HTTP_METHODS[func.__name__] = request_method_list

        @wraps(func)
        @django_require_http_methods(request_method_list)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    return decorator


def require_content_type(content_type_list: list[str] = None):
    """
    Logs API invocations with a wrong or missing content type header.
    This decorator may reject requests that do not have one of the required content types.

    If you do not specify a list of content-types as the first and only parameter, application/json is assumed
    """
    if content_type_list is None:
        content_type_list = ["application/json"]

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.content_type is None or request.content_type == "":
                logger.info(
                    "MissingContentType: %s %s was called without a Content-Type header"
                    % (request.method, request.path)
                )
            elif request.content_type not in content_type_list:
                logger.info(
                    "InvalidContentType: %s %s was called with %s, expected one of %s"
                    % (
                        request.method,
                        request.path,
                        request.content_type,
                        ",".join(content_type_list),
                    )
                )
            return func(request, *args, **kwargs)

        return inner

    return decorator


def require_server_access():
    """
    Decorator that checks if the user has permission to access the current server.

    This decorator verifies that:
    1. The user is authenticated
    2. If the user has server-specific permissions configured, they must have
       permission for the current server number
    3. Superusers always have access to all servers

    Returns a 403 Forbidden response if the user doesn't have access.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            # Allow unauthenticated requests to pass through
            # (they will be handled by @login_required or other auth decorators)
            if not request.user or not request.user.is_authenticated:
                return func(request, *args, **kwargs)

            # Superusers always have access
            if request.user.is_superuser:
                return func(request, *args, **kwargs)

            # Get the current server number from environment
            try:
                current_server_number = int(os.getenv("SERVER_NUMBER", "1"))
            except (ValueError, TypeError):
                logger.error("Invalid SERVER_NUMBER environment variable")
                current_server_number = 1

            # Import here to avoid circular imports
            from .models import UserServerPermission

            # Check if user has any server-specific permissions configured
            user_permissions = UserServerPermission.objects.filter(user=request.user)

            if user_permissions.exists():
                # User has specific server permissions configured
                # Check if they have permission for this server
                allowed_server_numbers = set(
                    perm.server_number for perm in user_permissions
                )

                if current_server_number not in allowed_server_numbers:
                    logger.warning(
                        f"User {request.user.username} attempted to access server {current_server_number} "
                        f"but only has permission for servers: {allowed_server_numbers}"
                    )
                    return JsonResponse(
                        {
                            "result": None,
                            "command": func.__name__,
                            "failed": True,
                            "error": f"You do not have permission to access server {current_server_number}. "
                                   f"Contact an administrator if you believe this is an error.",
                        },
                        status=403,
                    )

            # User has no specific permissions configured (can access all servers)
            # or has permission for this server
            return func(request, *args, **kwargs)

        return inner

    return decorator
