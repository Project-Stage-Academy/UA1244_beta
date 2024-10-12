from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences, Startup, Investor
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer, InvestorNotificationPrefsSerializer, TriggerNotificationSerializer
from .tasks import trigger_notification_task
from .permissions import IsInvestor, IsStartup
from django.core.exceptions import ValidationError


def create_error_response(message, status_code):
    """
    Helper function to create a standardized error response.

    Args:
        message (str or dict): The error message or dictionary of errors to return in the response.
        status_code (int): The HTTP status code for the response.

    Returns:
        Response: A DRF Response object with the error message and status code.
    """
    if isinstance(message, str):
        return Response({'error': message}, status=status_code)
    return Response(message, status=status_code)


def get_user_role_and_object(user):
    """
    Helper function to get the user's role (investor/startup) and corresponding object.
    
    Args:
        user: The authenticated user.
    
    Returns:
        tuple: The role ('investor' or 'startup') and the corresponding object (Investor or Startup).
    """
    if hasattr(user, 'investor'):
        return 'investor', user.investor
    elif hasattr(user, 'startup'):
        return 'startup', user.startup
    return None, None


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsInvestor | IsStartup]

    def get_queryset(self):
        """
        Returns the notifications related to the authenticated user, either as an investor or startup.
        Optimizes the query by using select_related to prefetch related models.
        
        Returns:
            QuerySet: The notifications related to the user or none if they are neither an investor nor startup.
        """
        user = self.request.user
        if hasattr(user, 'investor'):
            return Notification.objects.filter(investor=user.investor).select_related('investor', 'startup')
        elif hasattr(user, 'startup'):
            return Notification.objects.filter(startup=user.startup).select_related('investor', 'startup')
        return Notification.objects.none()

    def perform_update(self, serializer):
        """
        Marks a notification as read when it is updated.
        """
        instance = serializer.save()
        if not instance.is_read:
            instance.is_read = True
            instance.save()

    def perform_destroy(self, instance):
        """
        Deletes a notification.
        """
        instance.delete()

    @action(detail=False, methods=['post'], url_path='trigger')
    def trigger_notification(self, request):
        """
        Custom action to trigger a notification asynchronously.
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
    """
    permission_classes = [IsAuthenticated, IsInvestor | IsStartup]

    def get_preferences_and_serializer(self, user):
        """
        Helper function to get notification preferences and the corresponding serializer
        based on the user's role (investor or startup).

        Args:
            user: The authenticated user.

        Returns:
            tuple: The preferences instance and its corresponding serializer class.
        """
        if user.roles.filter(name='investor').exists():
            try:
                investor = Investor.objects.get(user=user)
                prefs, _ = InvestorNotificationPreferences.objects.get_or_create(investor=investor)
                return prefs, InvestorNotificationPrefsSerializer
            except Investor.DoesNotExist:
                raise ValidationError(f"Investor for user {user.email} not found.")

        elif user.roles.filter(name='startup').exists():
            try:
                startup = Startup.objects.get(user=user)
                prefs, _ = StartupNotificationPreferences.objects.get_or_create(startup=startup)
                return prefs, StartupNotificationPrefsSerializer
            except Startup.DoesNotExist:
                raise ValidationError(f"Startup for user {user.email} not found.")

        raise ValidationError("Notification preferences cannot be created for this user, as they are neither an investor nor a startup.")


    def create(self, request):
        """
        Creates notification preferences for the authenticated user based on their role.

        Returns:
            Response: The created or updated preferences, or a 400 error if validation fails.
        """
        try:
            prefs, serializer_class = self.get_preferences_and_serializer(request.user)
            serializer = serializer_class(prefs, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return create_error_response(str(e), status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        """
        Retrieves the notification preferences for the authenticated user.

        Returns:
            Response: The notification preferences for the user.
        """
        try:
            prefs, serializer_class = self.get_preferences_and_serializer(request.user)
            serializer = serializer_class(prefs)
            return Response(serializer.data)

        except ValidationError as e:
            return create_error_response(str(e), status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):
        """
        Updates notification preferences for the authenticated user.

        Returns:
            Response: The updated preferences or validation errors if any.
        """
        try:
            prefs, serializer_class = self.get_preferences_and_serializer(request.user)
            serializer = serializer_class(prefs, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return create_error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return create_error_response(str(e), status.HTTP_400_BAD_REQUEST)


class MarkAsReadView(APIView):
    """
    API View to mark a specific notification as read.
    """
    permission_classes = [IsAuthenticated, IsInvestor | IsStartup]

    def post(self, request, notification_id):
        """
        Marks a specific notification as read if the user has permission.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            self.check_object_permissions(request, notification)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)


class DeleteNotificationView(APIView):
    """
    API View to delete a specific notification.
    """
    permission_classes = [IsAuthenticated, IsInvestor | IsStartup]

    def delete(self, request, notification_id):
        """
        Deletes a specific notification if the user has permission.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            self.check_object_permissions(request, notification)
            notification.delete()
            return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return create_error_response('Notification not found', status.HTTP_404_NOT_FOUND)

