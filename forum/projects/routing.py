from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
        re_path(r'^ws/projects/(?P<project_id>[^/]+)/$', consumers.ProjectConsumer.as_asgi()),
]
