from django.urls import re_path

from communications.consumers import CommunicationConsumer, NotificationConsumer

websocket_urlpatterns = [
    # Route for chat functionality
    re_path(r'ws/communications/(?P<room_id>\w+)/$', CommunicationConsumer.as_asgi()),

    # Route for notifications
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', NotificationConsumer.as_asgi()),
]
