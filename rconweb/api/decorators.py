import logging
from functools import wraps

from django.views.decorators.http import (
    require_http_methods as django_require_http_methods,
)

logger = logging.getLogger("rconweb")

ENDPOINT_HTTP_METHODS: dict[str, list[str]] = {}


def require_http_methods(request_method_list: list[str]):
    def decorator(
        func,
    ):  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Any]:
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
