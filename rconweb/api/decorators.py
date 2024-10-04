import logging
from functools import wraps

from .utils import _get_data


logger = logging.getLogger("rconweb")

ENDPOINT_HTTP_METHODS: dict[str, list[str]] = {}


def require_http_methods(request_method_list: list[str]):
    # avoid circular imports
    from .auth import api_response

    def decorator(
        func,
    ):  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:
        if func.__name__ in ENDPOINT_HTTP_METHODS:
            raise ValueError(f"{func.__name__} already added to ENDPOINT_HTTP_METHODS")

        ENDPOINT_HTTP_METHODS[func.__name__] = request_method_list

        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_method_list:
                # No longer using django.views.decorators.http.require_http_methods
                # so we can return the same style response across the board
                data = _get_data(request)
                error = f"Method Not Allowed {request.method}: {request.path}"

                return api_response(
                    result=None,
                    failed=True,
                    arguments=data,
                    error=error,
                    status_code=405,
                )

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
