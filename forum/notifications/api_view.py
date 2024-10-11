from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences, Startup, Investor
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer, InvestorNotificationPrefsSerializer, TriggerNotificationSerializer
from .tasks import trigger_notification_task


def create_error_response(message, status_code):
    """
    Helper function to create a standardized error response.

    Args:
        message (str): The error message to return in the response.
        status_code (int): The HTTP status code for the response.

    Returns:
        Response: A DRF Response object with the error message and status code.
    """
    return Response({'error': message}, status=status_code)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.

    Methods:
        get_queryset(): Retrieves notifications based on the user's type (investor/startup).
        trigger_notification(): Custom action to asynchronously trigger a notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns the notifications related to the authenticated user, either as an investor or startup.

        Returns:
            QuerySet: The notifications related to the user or none if they are neither an investor nor startup.
        """
        user = self.request.user
        if hasattr(user, 'investor'):
            return Notification.objects.filter(investor=user.investor)
        elif hasattr(user, 'startup'):
            return Notification.objects.filter(startup=user.startup)
        return Notification.objects.none()

    def perform_update(self, serializer):
        """
        Marks a notification as read when it is updated.

        Args:
            serializer: The serializer used to save the notification instance.
        """
        instance = serializer.save()
        if not instance.is_read:
            instance.is_read = True
            instance.save()

    def perform_destroy(self, instance):
        """
        Deletes a notification.

        Args:
            instance: The notification instance to delete.
        """
        instance.delete()

    @action(detail=False, methods=['post'], url_path='trigger')
    def trigger_notification(self, request):
        """
        Custom action to trigger a notification asynchronously.

        Expects the following in the request body:
        - investor_id
        - startup_id
        - project_id
        - trigger_type

        Returns:
            Response: Message indicating that the notification trigger has been started.
        """
        serializer = TriggerNotificationSerializer(data=request.data)
        if serializer.is_valid():
            investor_id = serializer.validated_data['investor_id']
            startup_id = serializer.validated_data['startup_id']
            project_id = serializer.validated_data['project_id']
            trigger_type = serializer.validated_data['trigger_type']

            # Trigger the asynchronous task for notification
            trigger_notification_task.delay(investor_id, startup_id, project_id, trigger_type)

            return Response({'message': 'Notification trigger started'}, status=status.HTTP_200_OK)
        return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class NotificationPrefsViewSet(viewsets.ViewSet):
    """
    ViewSet for managing notification preferences for investors and startups.

    Methods:
        create(): Create notification preferences for authenticated user based on their role.
        list(): Retrieve notification preferences for the authenticated user.
        update(): Update notification preferences for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get_preferences_and_serializer(self, user):
        """
        Helper function to get notification preferences and the corresponding serializer based on the user's role.

        Args:
            user: The authenticated user.

        Returns:
            tuple: The preferences instance and its corresponding serializer class.
        """
        if hasattr(user, 'investor'):
            prefs, _ = InvestorNotificationPreferences.objects.get_or_create(investor=user.investor)
            return prefs, InvestorNotificationPrefsSerializer
        elif hasattr(user, 'startup'):
            prefs, _ = StartupNotificationPreferences.objects.get_or_create(startup=user.startup)
            return prefs, StartupNotificationPrefsSerializer
        return create_error_response("Notification preferences cannot be created for this user.", status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """
        Creates notification preferences for the authenticated user based on their role.

        If the user is either an investor or startup, the system will attempt to create or retrieve their preferences.
        If the user has no such role, it raises a validation error.

        Returns:
            Response: The created or updated preferences, or a 400 error if validation fails.
        """
        user = request.user

        # If the user is an investor, try to create or retrieve preferences
        if user.roles.filter(name='investor').exists():
            try:
                investor = Investor.objects.get(user=user)
                prefs, created = InvestorNotificationPreferences.objects.get_or_create(investor=investor)
            except Investor.DoesNotExist:
                return create_error_response(f"Investor for user {user.email} not found, preferences not created.", status.HTTP_400_BAD_REQUEST)

            serializer = InvestorNotificationPrefsSerializer(prefs, data=request.data)

        # If the user is a startup, try to create or retrieve preferences
        elif user.roles.filter(name='startup').exists():
            try:
                startup = Startup.objects.get(user=user)
                prefs, created = StartupNotificationPreferences.objects.get_or_create(startup=startup)
            except Startup.DoesNotExist:
                return create_error_response(f"Startup for user {user.email} not found, preferences not created.", status.HTTP_400_BAD_REQUEST)

            serializer = StartupNotificationPrefsSerializer(prefs, data=request.data)

        else:
            return create_error_response("Notification preferences cannot be created for this user, as they are neither an investor nor a startup.", status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Retrieves the notification preferences for the authenticated user.

        Returns:
            Response: The notification preferences for the user.
        """
        prefs, serializer_class = self.get_preferences_and_serializer(request.user)
        serializer = serializer_class(prefs)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Updates notification preferences for the authenticated user.

        Returns:
            Response: The updated preferences or validation errors if any.
        """
        prefs, serializer_class = self.get_preferences_and_serializer(request.user)
        serializer = serializer_class(prefs, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MarkAsReadView(APIView):
    """
    API View to mark a specific notification as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        """
        Marks a specific notification as read if the user has permission.

        Args:
            notification_id: The ID of the notification to mark as read.

        Returns:
            Response: A success message or an error if the notification was not found or permission denied.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            if (notification.startup and request.user == notification.startup.user) or \
               (notification.investor and request.user == notification.investor.user):
                notification.is_read = True
                notification.save()
                return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
            return create_error_response('Permission denied', status.HTTP_403_FORBIDDEN)
        except Notification.DoesNotExist:
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)


class DeleteNotificationView(APIView):
    """
    API View to delete a specific notification.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id):
        """
        Deletes a specific notification if the user has permission.

        Args:
            notification_id: The ID of the notification to delete.

        Returns:
            Response: A success message or an error if the notification was not found or permission denied.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            if (notification.startup and request.user == notification.startup.user) or \
               (notification.investor and request.user == notification.investor.user):
                notification.delete()
                return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            return create_error_response('Permission denied', status.HTTP_403_FORBIDDEN)
        except Notification.DoesNotExist:
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)
