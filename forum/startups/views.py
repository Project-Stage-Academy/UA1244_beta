from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import viewsets, status
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

