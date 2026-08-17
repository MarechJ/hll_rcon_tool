import ipaddress
import logging

logger = logging.getLogger("rconweb")


class XRealIpMiddleware:
    """Trust the `X-Real-IP` header set by the frontend nginx container as the
    client's real IP address.

    The frontend container's nginx only ever forwards this header with a
    value taken from `RCONWEB_REAL_IP_HEADER` (e.g. `CF-Connecting-IP` or
    `X-Forwarded-For` when CRCON sits behind a reverse proxy or a Cloudflare
    Tunnel) if the *direct* connection to nginx came from an address listed
    in `RCONWEB_TRUSTED_PROXIES`. Otherwise nginx sets `X-Real-IP` to the
    address of whoever connected to it directly. That means by the time a
    request reaches Django, `X-Real-IP` can always be trusted as the real
    client IP, without Django needing to re-implement its own trusted proxy
    list - see rcongui/nginx.conf and rcongui/entrypoint.sh.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        real_ip = request.META.get("HTTP_X_REAL_IP")
        if real_ip:
            real_ip = real_ip.strip()
            try:
                # Guard against a malformed/spoofed header ending up in
                # REMOTE_ADDR, since that value is used for rate limiting,
                # bans, and logging.
                ipaddress.ip_address(real_ip)
            except ValueError:
                logger.warning("Ignoring invalid X-Real-IP header value: %r", real_ip)
            else:
                request.META["REMOTE_ADDR"] = real_ip

        return self.get_response(request)
