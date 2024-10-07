from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin, IsOwner
from rest_framework.throttling import AnonRateThrottle


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    ViewSet for managing user retrieval and updating operations.

    This viewset handles the following operations:
    - Retrieve a user (`retrieve`): Requires the user to be authenticated and to either be the owner or an admin.
    - Update a user (`update`, `partial_update`): Requires the user to be authenticated and to be the owner of the account.
    - List users (`list`): Requires admin privileges.
    - Default: Requires authentication.

    Attributes:
        queryset (QuerySet): The queryset used for retrieving users.
        serializer_class (Serializer): The serializer class used for serializing user data.
        authentication_classes (list): List of authentication methods used for this viewset.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Get permissions based on the action being performed.

        Returns:
            list: List of permission instances required for the current action.
        """
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsOwner | IsAdmin]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for registering new users.

    This viewset allows new users to register through the API.
    - `create`: Registers a new user. Anyone can access this endpoint, but it is rate limited.

    Attributes:
        queryset (QuerySet): The queryset used for retrieving users.
        serializer_class (Serializer): The serializer class used for serializing user data.
        permission_classes (list): List of permissions used for this viewset.
        throttle_classes (list): List of throttling classes used to limit the rate of requests.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Create a new user and generate authentication tokens.

        Args:
            request (Request): The HTTP request object containing the user's registration data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A Response object containing the newly created user's data and authentication tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the newly registered user
        refresh = RefreshToken.for_user(user)
        response_data = {
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)