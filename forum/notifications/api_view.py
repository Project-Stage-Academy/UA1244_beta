from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer, InvestorNotificationPrefsSerializer
from rest_framework.views import APIView
from .models import Project
from notifications.utils import trigger_notification

class FollowProjectView(APIView):
    """
    API View for an investor to follow a project.
    """

    def post(self, request, project_id):
        investor = request.user.investor_profile  
        try:
            project = Project.objects.get(id=project_id)
            startup = project.startup

            project.followers.add(investor)
            project.save()

            trigger_notification(investor=investor, startup=startup, project=project, trigger_type='project_follow')

            return Response({'message': 'Followed the project'}, status=status.HTTP_201_CREATED)

        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

class NotificationListView(generics.ListAPIView):
    """
    View for listing notifications of the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'investor'):
            return Notification.objects.filter(investor=user.investor)
        elif hasattr(user, 'startup'):
            return Notification.objects.filter(startup=user.startup)
        return Notification.objects.none()

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

    def get_serializer_class(self):
        user = self.request.user
        if hasattr(user, 'investor'):
            return InvestorNotificationPrefsSerializer
        return StartupNotificationPrefsSerializer
    

class MarkNotificationAsReadView(APIView):
    """
    API View to mark a notification as read.
    """

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, startup=request.user.startup_profile)

            notification.is_read = True
            notification.save()

            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)

        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)