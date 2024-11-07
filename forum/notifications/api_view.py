"""
API views for notifications management.

This module provides API views for managing notifications and notification preferences
for 'Investor' and 'Startup' roles, including marking notifications as read, 
deleting notifications, and triggering new notifications.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import (
    Notification, StartupNotificationPreferences, InvestorNotificationPreferences,
    Startup, Investor
)
from .serializers import (
    NotificationSerializer, StartupNotificationPrefsSerializer,
    InvestorNotificationPrefsSerializer, TriggerNotificationSerializer
)
from .tasks import trigger_notification_task
from .permissions import IsInvestorOrStartup


def create_error_response(message, status_code):
    """
    Creates a standardized error response.

    Args:
        message (str or dict): Error message or dictionary of errors.
        status_code (int): HTTP status code for the response.

    Returns:
        Response: A DRF Response object with the error message and status code.
    """
    if isinstance(message, str):
        return Response({'error': message}, status=status_code)
    return Response(message, status=status_code)


def get_user_role_and_object(user):
    """
    Retrieves the roles and corresponding objects (Investor, Startup) for the given user.

    Args:
        user: The authenticated user.

    Returns:
        dict: A dictionary with roles ('investor', 'startup') as keys and corresponding objects as values.
    """
    roles_and_objects = {}

    if user.roles.filter(name='investor').exists():
        try:
            investor = Investor.objects.get(user=user)
            roles_and_objects['investor'] = investor
        except Investor.DoesNotExist:  # pylint: disable=no-member
            roles_and_objects['investor'] = None

    if user.roles.filter(name='startup').exists():
        try:
            startup = Startup.objects.get(user=user)
            roles_and_objects['startup'] = startup
        except Startup.DoesNotExist:  # pylint: disable=no-member
            roles_and_objects['startup'] = None

    return roles_and_objects if roles_and_objects else {}


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications, allowing CRUD operations and custom actions.

    Permissions:
        Only authenticated users with 'investor' or 'startup' roles can access this view.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsInvestorOrStartup]

    def get_queryset(self):
        """
        Retrieves notifications for the current user based on their roles.

        Returns:
            QuerySet: Notifications related to the investor or startup roles of the user.
        """
        user = self.request.user
        return Notification.objects.filter(
            Q(investor__in=user.investors.all()) | Q(startup__in=user.startups.all())
        )

    def perform_update(self, serializer):
        """
        Marks a notification as read when updated.

        Args:
            serializer: The serializer for the notification instance.
        """
        instance = serializer.save()
        if not instance.is_read:
            instance.is_read = True
            instance.save()

    def perform_destroy(self, instance):
        """
        Deletes a notification.

        Args:
            instance: The notification instance to be deleted.
        """
        instance.delete()

    @action(detail=False, methods=['post'], url_path='trigger')
    def trigger_notification(self, request):
        """
        Triggers a notification asynchronously for a specific investor and startup.

        Args:
            request: The HTTP request containing the necessary data to trigger the notification.

        Returns:
            Response: A response indicating that the notification trigger has been started.
        """
        serializer = TriggerNotificationSerializer(data=request.data)
        if serializer.is_valid():
            investor_id = serializer.validated_data['investor_id']
            startup_id = serializer.validated_data['startup_id']
            project_id = serializer.validated_data['project_id']
            trigger_type = serializer.validated_data['trigger_type']

            trigger_notification_task.delay(investor_id, startup_id, project_id, trigger_type)
            return Response({'message': 'Notification trigger started'}, status=status.HTTP_200_OK)

        return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class NotificationPrefsViewSet(viewsets.ViewSet):
    """
    ViewSet for managing notification preferences for both investors and startups.

    Permissions:
        Only authenticated users with 'investor' or 'startup' roles can access this view.
    """
    permission_classes = [IsAuthenticated, IsInvestorOrStartup]

    def get_preferences_and_serializer(self, user):
        """
        Retrieves the notification preferences and corresponding serializer class based on the user's role.

        Args:
            user: The authenticated user.

        Returns:
            list: A list of tuples containing preferences instances and their respective serializer classes.
        """
        preferences = []

        if user.roles.filter(name='investor').exists():
            try:
                investor = Investor.objects.get(user=user)
                prefs, _ = InvestorNotificationPreferences.objects.get_or_create(investor=investor)
                preferences.append((prefs, InvestorNotificationPrefsSerializer))
            except Investor.DoesNotExist:  # pylint: disable=no-member
                raise ValidationError(f"Investor for user {user.email} not found.")

        if user.roles.filter(name='startup').exists():
            try:
                startup = Startup.objects.get(user=user)
                prefs, _ = StartupNotificationPreferences.objects.get_or_create(startup=startup)
                preferences.append((prefs, StartupNotificationPrefsSerializer))
            except Startup.DoesNotExist:  # pylint: disable=no-member
                raise ValidationError(f"Startup for user {user.email} not found.")

        if not preferences:
            raise ValidationError("Notification preferences cannot be created for this user.")

        return preferences

    def create(self, request):
        """
        Creates or updates the notification preferences for the user.

        Args:
            request: The HTTP request containing the data to update preferences.

        Returns:
            Response: A response indicating the success or failure of the operation.
        """
        try:
            preferences = self.get_preferences_and_serializer(request.user)
            response_data = []

            for prefs, serializer_class in preferences:
                serializer = serializer_class(prefs, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return create_error_response(str(e), status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Retrieves the notification preferences for the user.

        Args:
            request: The HTTP request for retrieving preferences.

        Returns:
            Response: A response containing the user's notification preferences.
        """
        try:
            preferences = self.get_preferences_and_serializer(request.user)
            response_data = [serializer_class(prefs).data for prefs, serializer_class in preferences]
            return Response(response_data)
        except ValidationError as e:
            return create_error_response(str(e), status.HTTP_400_BAD_REQUEST)


class MarkAsReadView(APIView):
    """
    API View for marking a specific notification as read.

    Permissions:
        Only authenticated users with 'investor' or 'startup' roles can access this view.
    """
    permission_classes = [IsAuthenticated, IsInvestorOrStartup]

    def post(self, request, notification_id):
        """
        Marks a notification as read for the authenticated user.

        Args:
            request: The HTTP request to mark the notification as read.
            notification_id: The ID of the notification to mark as read.

        Returns:
            Response: A success message if the notification is marked as read, otherwise an error response.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        
        except Notification.DoesNotExist:  # pylint: disable=no-member
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)


class DeleteNotificationView(APIView):
    """
    API View for deleting a specific notification.

    Permissions:
        Only authenticated users with 'investor' or 'startup' roles can access this view.
    """
    permission_classes = [IsAuthenticated, IsInvestorOrStartup]

    def delete(self, request, notification_id):
        """
        Deletes a notification for the authenticated user.

        Args:
            request: The HTTP request to delete the notification.
            notification_id: The ID of the notification to delete.

        Returns:
            Response: A success message if the notification is deleted, otherwise an error response.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Notification.DoesNotExist:  # pylint: disable=no-member
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)
