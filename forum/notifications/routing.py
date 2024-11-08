"""
WebSocket routing configuration for notifications.

This module defines the WebSocket URL patterns for the NotificationConsumer,
allowing real-time notifications for authenticated users.
"""

from django.urls import re_path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
