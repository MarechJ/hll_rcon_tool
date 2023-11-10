"""
ASGI config for rconweb project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from api.websockets import urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rconweb.settings")
django_asgi_app = get_asgi_application()

from api.auth import APITokenAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": APITokenAuthMiddleware(URLRouter(urlpatterns)),
    }
)
