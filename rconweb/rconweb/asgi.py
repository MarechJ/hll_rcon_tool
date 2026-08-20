"""
ASGI config for rconweb project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rconweb.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

def get_application():
    # These modules access Django settings during import.
    from api import barricade, log_stream

    return ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": URLRouter(log_stream.urlpatterns + barricade.urlpatterns),
        }
    )


application = get_application()
