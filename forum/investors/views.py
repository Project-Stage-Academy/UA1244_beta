from django.shortcuts import HttpResponse
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Startup, Investor, InvestorFollow
from notifications.models import Notification
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from django.db.utils import IntegrityError as DBIntegrityError


logger = logging.getLogger(__name__)


def investors(request):
    try:
        logger.info("Processing the request.")
        return HttpResponse("Not implemented")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

class InvestorNotificationsAPIView(APIView):
    """
    API view to retrieve unread notifications for an authenticated investor.

    This view retrieves all unread notifications for the currently authenticated 
    investor, ordered by the most recent notification first. It requires the 
    user to be authenticated.

    Attributes:
        permission_classes (list): Ensures that only authenticated users can access this view.

    Methods:
        get(request):
            Retrieves unread notifications for the authenticated investor.
            Returns a serialized list of notifications with HTTP status 200 if 
            notifications are found.
            Returns an error message with HTTP status 404 if no notifications exist.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            investor = Investor.objects.get(user=request.user)
            notifications = Notification.objects.filter(investor=investor, is_read=False).order_by('-date_time')
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "No notifications found."}, status=status.HTTP_404_NOT_FOUND)


class SaveStartupView(APIView):
    """
    API view for saving or following a startup by an investor.

    This view handles POST requests from authenticated investors, allowing them
    to save (follow) a startup by providing the startup's ID in the URL.

    - If the authenticated user is not an investor, or if the startup with the
      given ID does not exist, a 404 error is returned.
    - If the investor has already saved the startup, a 400 response is returned
      with a message indicating the startup has already been saved.
    - If the save operation is successful, a 201 response is returned with a
      success message.
    - If an unexpected error occurs during the save operation, a 500 error
      response is returned.

    Attributes:
        permission_classes (list): List of permissions required for this view.
            In this case, it ensures that the user must be authenticated.

    Methods:
        post(request, startup_id):
            Handles the POST request to save the startup. The investor and startup
            are fetched using the logged-in user and the provided startup ID.
            If successful, the investor's follow of the startup is saved, otherwise
            appropriate error responses are returned.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        try:
            investor = Investor.objects.get(user=request.user)
            startup = Startup.objects.get(pk=startup_id)
        except Investor.DoesNotExist:
            return Response({'detail': 'Investor not found'}, status=status.HTTP_404_NOT_FOUND)
        except Startup.DoesNotExist:
            return Response({'detail': 'Startup not found'}, status=status.HTTP_404_NOT_FOUND)

        if InvestorFollow.objects.filter(investor=investor, startup=startup).exists():
            return Response({'detail': 'You have already saved this startup.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            InvestorFollow.objects.create(investor=investor, startup=startup)
            return Response({'detail': 'Startup saved successfully.'}, status=status.HTTP_201_CREATED)

        except DBIntegrityError as e:
            if 'unique constraint' in str(e):
                return Response({'detail': 'This startup is already saved.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'A database error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
