import logging

from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Startup
from .serializers import StartupSerializer

class StartupViewSet(viewsets.ModelViewSet):
    """
    API view to handle CRUD operations for Startup instances.
    This view provides GET, POST, PUT methods 
    to list, create, update startup profiles. 
    It requires the user to be authenticated.
    
    Attributes:
        queryset (QuerySet): A queryset of all Startup instances.
        serializer_class (Serializer): The serializer used to validate 
        and serialize data.
        permission_classes (list): A list of permission classes 
        that determine access rights.
    """
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new Startup instance.

        This method handles the creation of a new startup profile. 
        It validates the input data and returns the created instance 
        or an error message if validation fails.

        Args:
            request (Request): The request object containing data to create the startup.

        Returns:
            Response: A response containing the created startup data or error details.
        """
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "Database integrity error occurred."},
                             status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update an existing Startup instance.

        This method handles the updating of an existing startup profile. 
        It validates the input data and returns the updated instance 
        or an error message if validation fails.

        Args:
            request (Request): The request object containing updated data for the startup.

        Returns:
            Response: A response containing the updated startup data or error details.
        """
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "Database integrity error occurred."},
                             status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a Startup instance.

        This method handles the deletion of a startup profile. 
        It returns a success response if the deletion is successful 
        or an error message if the instance does not exist or if 
        there are integrity constraints.

        Args:
            request (Request): The request object containing the ID of the startup to delete.

        Returns:
            Response: A response with status 204 if deletion was successful, 
            or error details if there was an issue.
        """
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"detail": "Startup not found."}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return Response({"detail": "Unable to delete the startup due to integrity constraints."},
                             status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)


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
