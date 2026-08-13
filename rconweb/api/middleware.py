import logging
import os

logger = logging.getLogger("rconweb")


class ClientIpHeaderMiddleware:
    """
    Rewrites ``request.META["REMOTE_ADDR"]`` using the value of a
    configurable HTTP header, so that ``django-ratelimit`` (and anything
    else in Django that relies on ``REMOTE_ADDR``, e.g. IP bans) sees the
    real client IP when CRCON is running behind a reverse proxy / load
    balancer, rather than the IP of the proxy itself.

    Configure the header to trust via the ``CLIENT_IP_HEADER`` environment
    variable, using the normal HTTP header name, e.g.::

        CLIENT_IP_HEADER=X-Forwarded-For
        CLIENT_IP_HEADER=X-Real-IP
        CLIENT_IP_HEADER=CF-Connecting-IP

    Leave ``CLIENT_IP_HEADER`` unset/empty (the default) to disable this
    middleware entirely; ``REMOTE_ADDR`` is then left untouched, which is
    whatever your WSGI/ASGI server set it to (typically the IP of whatever
    connected directly to it).

    SECURITY WARNING: only enable this if CRCON is actually behind a
    reverse proxy that you control, and that proxy always sets/overwrites
    this header itself (i.e. it strips/ignores any value a client tries to
    send for it). Otherwise a client could simply set this header on their
    request and spoof any IP they like, bypassing rate limiting and IP
    based bans.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        header = (os.getenv("CLIENT_IP_HEADER") or "").strip()
        # Django exposes HTTP headers on request.META using the
        # "HTTP_HEADER_NAME" convention (uppercased, dashes -> underscores)
        self.meta_key = "HTTP_" + header.upper().replace("-", "_") if header else None

        if self.meta_key:
            logger.info(
                "ClientIpHeaderMiddleware enabled: REMOTE_ADDR will be set from the '%s' header (%s)",
                header,
                self.meta_key,
            )

    def __call__(self, request):
        if self.meta_key:
            value = request.META.get(self.meta_key)
            if value:
                # Headers such as X-Forwarded-For can contain a comma
                # separated chain of IPs (client, proxy1, proxy2, ...).
                # The left-most entry is the original client IP.
                ip = value.split(",")[0].strip()
                if ip:
                    request.META["REMOTE_ADDR"] = ip

        return self.get_response(request)
