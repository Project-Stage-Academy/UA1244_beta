"""
URL configuration for the Notifications app.

Includes routes for notification CRUD operations, marking notifications as read,
deleting notifications, and updating notification preferences.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_view import (
    NotificationViewSet,
    NotificationPrefsViewSet,
    MarkAsReadView,
    DeleteNotificationView
)
from .views import NotificationPreferencesUpdateView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-prefs', NotificationPrefsViewSet, basename='notificationpreferences')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'notifications/mark-read/<int:notification_id>/',
        MarkAsReadView.as_view(),
        name='mark-as-read'
    ),
    path(
        'notifications/delete/<int:notification_id>/',
        DeleteNotificationView.as_view(),
        name='delete-notification'
    ),
    path(
        'profile/notifications/',
        NotificationPreferencesUpdateView.as_view(),
        name='notification-prefs-update'
    ),
    path(
    'notifications/trigger/',
    NotificationViewSet.as_view({'post': 'trigger_notification'}),
    name='notification-trigger'
),
]

