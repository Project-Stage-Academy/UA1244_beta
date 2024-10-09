from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin, IsOwner
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.throttling import AnonRateThrottle
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

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

        refresh = RefreshToken.for_user(user)
        response_data = {
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    


class ActivateAccountView(APIView):
    """
    API View for activating a user's account via a token.

    This view takes a token from the URL, verifies it, and activates the user's account by setting is_active to True.

    Permission Classes:
        - Allows any user to access this view (AllowAny).

    Methods:
        get(request, token):
            Activates the user's account if the token is valid and the account is not already active.
    """
    
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]  

    def get(self, request, token, *args, **kwargs):
        """
        Handle GET requests to activate a user's account.

        Args:
            request (Request): The HTTP request object.
            token (str): The activation token passed in the URL.

        Returns:
            Response: A Response object indicating success or failure of activation.
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')

            user = User.objects.get(user_id=user_id)

            if user.is_active:
                return Response({'message': 'Account is already activated'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            return Response({'message': 'Account successfully activated'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        except AuthenticationFailed:
            return Response({'error': 'Invalid or expired token. Please request a new activation link.'}, status=status.HTTP_400_BAD_REQUEST)

        except TokenError as e:
            return Response({'error': f'Token error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)