import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

from communications.consumers import CommunicationConsumer
from projects.routing import websocket_urlpatterns
from django.urls import path
from communications.consumers import CommunicationConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

"""
ASGI application routing configuration.

This application routes HTTP and WebSocket requests to the appropriate
ASGI application. It uses Django's `get_asgi_application` for HTTP
routing and the `AuthMiddlewareStack` along with a URL router for
WebSocket connections.

Attributes:
    application (ASGI application): The ASGI application that routes
    incoming HTTP and WebSocket requests.
"""

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                *websocket_urlpatterns,
                re_path(r"ws/communications/(?P<room_id>\w+)/$", CommunicationConsumer.as_asgi())
            ]
        )
    )
})
