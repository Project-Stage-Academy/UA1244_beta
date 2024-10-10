from django.urls import path
from .api_view import NotificationListView, NotificationPrefsViewSet, MarkNotificationAsReadView, FollowProjectView

app_name = 'notifications'

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('preferences/', NotificationPrefsViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='notification_prefs'),
    path('notifications/read/<int:notification_id>/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),
    path('projects/<uuid:project_id>/follow/', FollowProjectView.as_view(), name='follow_project'),
]