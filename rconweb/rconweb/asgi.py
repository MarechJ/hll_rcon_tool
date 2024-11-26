"""
ASGI config for rconweb project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rconweb.settings")
django_asgi_app = get_asgi_application()

# This has to be imported *after* setting DJANGO_SETTINGS_MODULE
from api import barricade, log_stream

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(log_stream.urlpatterns + barricade.urlpatterns),
    }
)
