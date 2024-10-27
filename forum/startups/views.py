from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Startup
from investors.models import Investor, InvestorFollow
from .serializers import StartupSerializer
import logging

logger = logging.getLogger(__name__)


class BaseInvestorView(APIView):
    permission_classes = [IsAuthenticated]

    def get_investor(self, request):
        try:
            return Investor.objects.get(user=request.user)
        except Investor.DoesNotExist:
            logger.warning(f"Invesotor not found for user ID {request.user.id}")
            return None


class SavedStartupsListAPIView(BaseInvestorView):
    """
    API endpoint for listing all startups an investor has saved.

    Permissions:
        - Requires the user to be authenticated.

    Methods:
        - GET: Retrieves and returns a list of startups that the authenticated investor has saved.
        
    Workflow:
        1. The view first retrieves the `Investor` instance associated with the authenticated user.
        2. It then filters startups linked to the investor in the `InvestorFollow` model.
        3. The filtered startups are serialized and returned as a JSON response.
        
    Responses:
        - 200 OK: Returns a list of saved startups if the investor is found.
        - 404 Not Found: Returns an error message if the investor does not exist.
    """

    def get(self, request):
        investor = self.get_investor(request)
        if investor is None:
            return Response({"error": "Invesotor not found."}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        saved_startups = Startup.objects.prefetch_related('startup_investors').filter(startup_investors__investor=investor)
        paginated_startups = paginator.paginate_queryset(saved_startups, request)
        serializer = StartupSerializer(paginated_startups, many=True)

        logger.info(f"Returned saved startups for investor ID {investor.investor_id}")
        return paginator.get_paginated_response(serializer.data)


class UnfollowStartupAPIView(BaseInvestorView):
    """
    API endpoint for unfollowing (or removing) a saved startup for an investor.

    Permissions:
        - Requires the user to be authenticated.

    Methods:
        - DELETE: Allows an investor to unfollow a specific startup by ID.
        
    Workflow:
        1. The view first retrieves the `Investor` instance associated with the authenticated user.
        2. It checks for the existence of the startup in the investor’s saved list.
        3. If found, the saved entry is deleted from the `InvestorFollow` model.
        
    Responses:
        - 204 No Content: Indicates successful unfollowing.
        - 404 Not Found: Returns an error if the investor or follow record does not exist.
    """

    def delete(self, request, startup_id):
        investor = self.get_investor(request)
        if investor is None:
            return Response({"error": "Investor not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            follow = InvestorFollow.objects.get(investor=investor, startup_id=startup_id)
            follow.delete()
            logger.info(f"Investor ID {investor.investor_id} unfollowed startup ID {startup_id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except InvestorFollow.DoesNotExist:
            logger.warning(f"Startup ID {startup_id} not followed by investor ID {investor.investor_id}")
            return Response({"error": "Startup not followed."}, status=status.HTTP_404_NOT_FOUND)


def create_error_response(message, status_code):
    """
    Creates a standardized error response for various views.

    Args:
        message (str): The error message to return in the response.
        status_code (int): The HTTP status code to include in the response.

    Returns:
        Response: A DRF Response object containing the error message and status code.
    """
    return Response({'error': message}, status=status_code)


class StartupListView(generics.ListAPIView):
    """
    API View to retrieve a list of all startup objects.

    Permissions:
        - Only authenticated users can access this view.

    Methods:
        - get_queryset(): Retrieves all startup objects from the database.
        - get(): Handles GET requests to fetch and return the list of startups.
    """
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves all startup objects from the database.

        Returns:
            QuerySet: A queryset containing all startup objects.
        """
        return Startup.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve the list of startups.

        Returns:
            Response: A DRF Response containing serialized startup data or an error message if no startups are found.
        """
        try:
            startups = self.get_queryset()
            if not startups.exists():
                return create_error_response("No startups found.", status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(startups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            return create_error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartupDetailView(generics.RetrieveAPIView):
    """
    API View to retrieve detailed information about a specific startup.

    Permissions:
        - Only authenticated users can access this view.

    Attributes:
        - queryset: A queryset of all startup objects.
        - serializer_class: Specifies the serializer used to convert model instances to JSON.
        - lookup_field: The field used to retrieve a specific startup (e.g., 'startup_id').

    Methods:
        - get_queryset(): Retrieves all startup objects from the database.
        - get(): Handles GET requests to retrieve details about a specific startup by ID.
    """
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    lookup_field = 'startup_id'

    def get_queryset(self):
        """
        Retrieves all startup objects from the database.

        Returns:
            QuerySet: A queryset containing all startup objects.
        """
        return Startup.objects.all()

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve details about a specific startup by its ID.

        Args:
            request: The HTTP request object.
            startup_id: The ID of the startup to retrieve.

        Returns:
            Response: A DRF Response containing serialized startup data or an error message if not found.
        """
        try:
            startup_id = kwargs.get('startup_id')
            if not startup_id:
                return create_error_response("Missing startup ID in the URL", status.HTTP_400_BAD_REQUEST)

            startup = self.get_object()
            serializer = self.get_serializer(startup)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            logger.error(f"Startup with id {startup_id} not found.")
            return create_error_response("Startup not found", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return create_error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendMessageView(generics.CreateAPIView):
    """
    API View to handle sending messages to a specific startup.

    Permissions:
        - Only authenticated users can send messages.

    Methods:
        - post(): Handles POST requests to send a message to the specified startup.
    """
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to send a message to a startup.

        Args:
            request: The HTTP request object containing the 'startup_id' and 'content' of the message.

        Returns:
            Response: A success message upon sending the message or an error message if validation fails.
        """
        startup_id = request.data.get('startup_id')
        content = request.data.get('content')

        if not startup_id or not content:
            return create_error_response("Startup ID and content are required.", status.HTTP_400_BAD_REQUEST)

        try:
            startup = Startup.objects.get(pk=startup_id)
            # Логіка для збереження повідомлення
            return Response({"success": f"Message sent to {startup.company_name}"})
        except Startup.DoesNotExist:
            return create_error_response("Startup not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return create_error_response(f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
