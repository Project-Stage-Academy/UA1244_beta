from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer, InvestorNotificationPrefsSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications: listing, marking as read, and deleting notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return notifications for the authenticated user (either investor or startup).
        """
        user = self.request.user
        if hasattr(user, 'investor'):
            return Notification.objects.filter(investor=user.investor)
        elif hasattr(user, 'startup'):
            return Notification.objects.filter(startup=user.startup)
        return Notification.objects.none()

    def perform_update(self, serializer):
        """
        Custom update method to mark notification as read if not already.
        """
        instance = serializer.save()
        if not instance.is_read:
            instance.is_read = True
            instance.save()

    def perform_destroy(self, instance):
        """
        Custom delete method to destroy the notification.
        """
        instance.delete()


class MarkAsReadView(APIView):
    """
    API View to mark a specific notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)

            if (notification.startup and request.user == notification.startup.user) or \
               (notification.investor and request.user == notification.investor.user):
                notification.is_read = True
                notification.save()
                return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class DeleteNotificationView(APIView):
    """
    API View to delete a specific notification.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id):
        try:
            # Fetch the notification by its ID
            notification = Notification.objects.get(id=notification_id)

            # Ensure the user has permission to delete the notification
            if (notification.startup and request.user == notification.startup.user) or \
               (notification.investor and request.user == notification.investor.user):
                notification.delete()
                return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


class NotificationPrefsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences for Investors and Startups.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'investor'):
            return InvestorNotificationPreferences.objects.filter(investor=user.investor)
        elif hasattr(user, 'startup'):
            return StartupNotificationPreferences.objects.filter(startup=user.startup)
        return Notification.objects.none()

    def get_serializer_class(self):
        user = self.request.user
        if hasattr(user, 'investor'):
            return InvestorNotificationPrefsSerializer
        return StartupNotificationPrefsSerializer


class NotificationPreferencesUpdateView(View):
    def get(self, request):
        if not hasattr(request.user, 'startup'):
            messages.error(request, "Користувач не має стартапу.")
            return redirect('notification-prefs-update')
        startup = request.user.startup
        context = {
            'startup': startup
        }
        return render(request, 'notifications/preferences.html', context)

    def post(self, request):
        if not hasattr(request.user, 'startup'):
            messages.error(request, "Користувач не має стартапу.")
            return redirect('notification-prefs-update')
        startup = request.user.startup
        preferences = startup.notification_preferences

        preferences.email_project_updates = 'email_project_updates' in request.POST
        preferences.push_project_updates = 'push_project_updates' in request.POST
        preferences.email_startup_updates = 'email_startup_updates' in request.POST
        preferences.push_startup_updates = 'push_startup_updates' in request.POST

        preferences.save()
        messages.success(request, "Your notification preferences have been updated.")
        return redirect('notification-prefs-update')


class NotificationPreferenceAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = StartupNotificationPrefsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return StartupNotificationPreferences.objects.get_or_create(startup=self.request.user.startup)[0]
