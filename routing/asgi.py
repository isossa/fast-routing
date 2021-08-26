"""
ASGI config for routing project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routing.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from cvrp.middleware import websockets
import cvrp.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            cvrp.routing.websocket_urlpatterns
        )
    ),
})

# application = get_asgi_application()
# application = websockets(application)

