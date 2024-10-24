from django.urls import re_path
from . import consumers

"""
This module defines WebSocket URL patterns for the Django application.

WebSocket URL patterns are defined using `re_path` to route WebSocket connections
to the appropriate consumer based on the URL structure. Specifically, it routes
connections for project-specific WebSocket channels, where the project ID is
passed as a URL parameter.A
"""

websocket_urlpatterns = [
        re_path(r'^ws/projects/(?P<project_id>[^/]+)/$', consumers.ProjectConsumer.as_asgi()),
]
