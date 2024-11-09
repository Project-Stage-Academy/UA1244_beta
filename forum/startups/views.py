import logging
import traceback

from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend,
)

from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from .permissions import IsStartup, IsInvestor
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Startup, Industry
from investors.models import Investor, InvestorFollow
from .serializers import StartupSerializer, IndustrySerializer, StartupDocumentSerializer
from .document import StartupDocument



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class StartupViewSet(viewsets.ModelViewSet):
    """
    API view to handle CRUD operations for Startup instances.
    This view provides GET, POST, PUT, DELETE methods for managing 
    startup profiles in the system.This view set ensures that only 
    authenticated users with the correct role can perform 
    specific actions: investors have read access and startups have create, 
    update, and delete access. The view set includes custom error handling
    for database operations and supports filtering and search functionality.

    Attributes:
        queryset (QuerySet): The default queryset for retrieving Startup instances.
        serializer_class (Serializer): The serializer class used to validate and 
        serialize Startup data.

    Methods:
        get_permissions(): Determines the permissions required for each action.
            Investors can access list and retrieve actions; startups can perform
            create, update, and delete actions.
        
        create(): Handles creating a new startup profile. It includes custom error 
            handling for validation and integrity errors, providing appropriate 
            error messages.

        update(): Handles updating an existing startup profile, with custom error
            handling for validation and integrity errors.

        destroy(): Handles deletion of a startup profile, with error handling for
            cases where the instance does not exist or cannot be deleted due to 
            database integrity constraints.

        retrieve(): Retrieves a single startup profile by its ID. Returns a 404 error if 
            the startup is not found.

        list(): Retrieves a list of all startup profiles to the investor. Includes error
            handling to return appropriate messages in case of any unexpected issues.

        get_queryset(): 
            Retrieves the queryset of startup profiles, applying custom filtering 
            based on the user's role and query parameters. Only investors can 
            access the data. Supports filtering by `company_name` and `industry_name` 
            and includes a search functionality for company names.

        filter_queryset(): 
            Filters and searches the queryset based on provided query parameters, 
            such as `search`, `company_name`, and `industry_name`. The method modifies 
            the queryset to match the provided criteria and returns the filtered queryset.
    """
    queryset = Startup.objects.all().order_by('company_name')
    serializer_class = StartupSerializer
    pagination_class = StandardResultsSetPagination
    

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsInvestor]
        else:
            permission_classes = [IsStartup]

        return [permission() for permission in permission_classes]
    
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
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific Startup instance by ID.
        
        This method handles the retrieval of a startup profile.
        It returns the startup data or an error message if any error occures.
        Args:
            request (Request): The request object to retrieve the startup.

        Returns:
            Response: A response containing the startup data or error details.
        
        Logs:
            Logs key actions such as the retrieval request, success, not found,
            and any errors that occur.
        """
        logger.info(f"Retrieve request for Startup ID: {kwargs.get('pk')}") 
        try:
            instance = self.get_object()
            logger.info(f"Successfully retrieved Startup: {instance.company_name}")
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            logger.warning(f"Startup with ID {kwargs.get('pk')} not found.")
            return Response({"detail": "Startup not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            logger.error(f"Validation error occurred: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.error("Database integrity error occurred during retrieval.")
            return Response({"detail": "Database integrity error occurred."},
                        status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        List all Startup instances.
        
        This method retrieves a list of all startups and handles any errors that
        may occur during retrieval.

        Args:
            request (Request): The request object to list startups.

        Returns:
            Response: A response containing the list of startups or error details.

        Logs:
            Logs key actions such as request details, total startups found, pagination status,
            and any errors that occur during the request processing.
        """
        logger.info(f"List request for all startups. Query params: {request.query_params}")
        try:
            queryset = self.get_queryset()
            logger.info(f"Total startups found: {queryset.count()}")
            page = self.paginate_queryset(queryset)
            if page is not None:
                logger.info(f"Returning paginated response with {len(page)} startups.")
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            logger.info("Returning non-paginated response for all startups.")
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Validation error occurred: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.error("Database integrity error occurred during listing.")
            return Response({"detail": "Database integrity error occurred."},
                        status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def filter_queryset(self, queryset):
        """
        Filters and searches the queryset based on the provided query parameters.

        This method is responsible for applying search and filtering options to the 
        queryset based on the query parameters `search`, `company_name`, and `industry_name`.
        It will modify the queryset to match the criteria provided by the user.

        Args:
            queryset (QuerySet): The original queryset of startup profiles that will 
            be filtered based on the query parameters.

        Returns:
            QuerySet: The filtered queryset, which can be further used for listing or retrieving 
            startup profiles.

        """
        search = self.request.query_params.get('search', None)
        company_name = self.request.query_params.get('company_name', None)
        industry_name = self.request.query_params.get('industry_name', None)

        if search:
            queryset = queryset.filter(company_name__icontains=search)
        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        if industry_name:
            queryset = queryset.filter(industries__name__icontains=industry_name)

        return queryset
    
    def get_queryset(self):
        """
        Retrieves the queryset of startup profiles and applies any custom filtering.

        Returns:
            QuerySet: The final queryset that includes all applied filters based
              on the user's query parameters.
        """
        queryset = super().get_queryset()
        return self.filter_queryset(queryset)


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
    API endpoint to retrieve a list of startups with optional filtering.
    """
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        industry_name = self.request.query_params.get("industry")
        location_city = self.request.query_params.get("location")
        
        queryset = Startup.objects.all()
        
        if industry_name:
            queryset = queryset.filter(industries__name__iexact=industry_name)

        if location_city:
            queryset = queryset.filter(location__city__iexact=location_city)
        
        return queryset

    def list(self, request, *args, **kwargs):
        logger.info("Received GET request for startup list")
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartupDetailView(generics.RetrieveAPIView):
    """
    API View to retrieve detailed information about a specific startup.
    """
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'startup_id'

    def retrieve(self, request, *args, **kwargs):
        startup_id = kwargs.get('startup_id')
        logger.info(f"Received GET request for startup detail with ID {startup_id}")
        try:
            startup = self.get_object()
            serializer = self.get_serializer(startup)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            logger.error(f"Startup with id {startup_id} not found.")
            return Response({"error": "Startup not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendMessageView(generics.CreateAPIView):
    """
    API View to handle sending messages to a specific startup.
    """
    permission_classes = [IsAuthenticated]

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
            return Response({"error": "Startup ID and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            startup = get_object_or_404(Startup, pk=startup_id)
            # Логіка для збереження повідомлення, наприклад, створення запису в базі даних
            # Message.objects.create(startup=startup, content=content, user=request.user)

            logger.info(f"Message sent to {startup.company_name}")
            return Response({"success": f"Message sent to {startup.company_name}"}, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            logger.error(f"Startup with ID {startup_id} not found.")
            return Response({"error": "Startup not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_industries_bulk(request):
    """
    Endpoint to retrieve a list of industries by their IDs.

    This endpoint accepts a POST request containing a list of industry IDs and returns
    the corresponding industry objects if they exist. It is intended to provide detailed information 
    about multiple industries in a single request, based on the provided IDs.

    Parameters:
    - ids (list of UUIDs): A list of industry IDs to retrieve. The IDs should be provided 
      in the request payload under the "ids" key.

    Returns:
    - 200 OK: A JSON response containing the details of the requested industries. Each industry 
      is serialized with its respective attributes.
    - 404 Not Found: If no industries are found with the provided IDs, a JSON response with 
      an error message is returned.
    - 400 Bad Request: If no industry IDs are provided in the request, a JSON response with 
      an error message is returned.

    Permissions:
    - Requires the user to be authenticated.
    """
    ids = request.data.get('ids', [])
    if not ids:
        return Response({"error": "No industry IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

    industries = Industry.objects.filter(industry_id__in=ids)
    
    if not industries.exists():
        return Response({"error": "No industries found for the provided IDs"}, status=status.HTTP_404_NOT_FOUND)

    serializer = IndustrySerializer(industries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class StartupSearchViewSet(DocumentViewSet):
    """
    ViewSet for searching Startup documents in Elasticsearch.
    Supports complex filtering, ordering, and compound searching on Startup attributes.
    """
    document = StartupDocument
    serializer_class = StartupDocumentSerializer
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]
    search_fields = ('company_name', 'description', 'industries.name')
    filter_fields = {
        'funding_stage': 'exact',
        'location.city': 'exact',
        'location.country': 'exact',
        'total_funding': {
            'lookup': 'range'
        },
    }
    ordering_fields = {
        'company_name': 'company_name.raw',
        'created_at': 'created_at',
        'total_funding': 'total_funding',
        'number_of_employees': 'number_of_employees',
    }
    ordering = ('created_at',)

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except ValueError as e:
            return Response({"error": f"Invalid value: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError as e:
            return Response({"error": f"Attribute error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected error in StartupSearchViewSet:")
            print(traceback.format_exc())
            return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)