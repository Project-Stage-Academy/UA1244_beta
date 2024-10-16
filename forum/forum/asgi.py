import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns
from communications.consumers import CommunicationConsumer
from django.urls import path, re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forum.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                *websocket_urlpatterns,
                *[path('ws/communications/', CommunicationConsumer.as_asgi()),]
            ]
        )
    ),
})
