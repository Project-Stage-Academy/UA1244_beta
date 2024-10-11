from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_view import NotificationViewSet, NotificationPrefsViewSet, MarkAsReadView, DeleteNotificationView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-prefs', NotificationPrefsViewSet, basename='notificationpreferences')

urlpatterns = [
    path('', include(router.urls)),
    path('notifications/mark-read/<int:notification_id>/', MarkAsReadView.as_view(), name='mark-as-read'),
    path('notifications/delete/<int:notification_id>/', DeleteNotificationView.as_view(), name='delete-notification'),
]