from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from .models import User, Role
from .serializers import UserSerializer
from .permissions import IsAdmin, IsOwner, IsInvestor, IsStartup
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from rest_framework.exceptions import NotFound
from .serializers import CustomToken

User = get_user_model()


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Manages user retrieval and updating operations.

    Operations:
    - Retrieve a user: Requires authentication and either owner or admin permissions.
    - Update a user: Requires authentication and ownership of the account.
    - List users: Requires admin privileges.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsOwner | IsAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class RegisterViewSet(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin):
    """
    Представлення для реєстрації нових користувачів.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
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


def create_error_response(message, status_code):
    """
    Centralizes error responses for various views.

    Args:
        message (str): The error message.
        status_code (int): The HTTP status code.

    Returns:
        Response: JSON response containing the error message and status code.
    """
    return Response({'error': message}, status=status_code)


class ActivateAccountView(APIView):
    """
    Activates a user's account via a token.

    Verifies the provided token and activates the user's account if valid.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, token, *args, **kwargs):
        try:
            activation_token = CustomToken(token)
            user_id = activation_token.get('user_id')

            user = User.objects.get(user_id=user_id)

            if user.is_active:
                return create_error_response('Account is already activated', status.HTTP_400_BAD_REQUEST)

            user.is_active = True

            roles = user.roles.all()
            if roles.count() == 1:
                user.active_role = roles[0]
            else:
                user.active_role = Role.objects.get(name='unassigned')

            user.save()

            return Response({'message': 'Account successfully activated'}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return create_error_response('User does not exist', status.HTTP_404_NOT_FOUND)
        except AuthenticationFailed:
            return create_error_response('Invalid or expired token. Please request a new activation link.', status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return create_error_response(f'Token error: {str(e)}', status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return create_error_response(f'Something went wrong: {str(e)}', status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignOutView(APIView):
    """
    Logs out the user by invalidating the access and refresh tokens.

    Tokens are invalidated by setting their expiration time to zero and deleting them from the client's cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            access_token = AccessToken(request.auth.token) if request.auth else None
            if access_token:
                access_token.set_exp(lifetime=timedelta(seconds=0))

            refresh_token = request.data.get('refresh')
            if refresh_token:
                refresh_token_instance = RefreshToken(refresh_token)
                refresh_token_instance.set_exp(lifetime=timedelta(seconds=0))

            response = Response({"message": "User successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response

        except TokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangeActiveRoleAPIView(APIView):
    """
    Allows users to change their active role.

    Changes the role based on the role name provided in the request data.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        role_name = request.data.get('role')

        if not role_name:
            return Response({"detail": "Role name is required."}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.filter(name=role_name).first()

        if not role:
            raise NotFound(detail=f"Role {role_name} does not exist.")

        request.user.change_active_role(role_name)

        return Response({"detail": f"Active role changed to {role_name}"}, status=status.HTTP_200_OK)


class InvestorOnlyView(APIView):
    """
    Provides access to content exclusive to investors.
    """
    permission_classes = [IsInvestor]

    def get(self, request):
        return Response({"message": "Welcome, Investor!"})


class StartupOnlyView(APIView):
    """
    Provides access to content exclusive to startups.
    """
    permission_classes = [IsStartup]

    def get(self, request):
        return Response({"message": "Welcome, Startup!"})
    




from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer  # Імпортуємо серіалізатор
from django.views.decorators.csrf import csrf_exempt



import logging

logger = logging.getLogger(__name__)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        logger.debug(f"Received login request with data: {request.data}")
        
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            data = {
                "email": user.email,
                "access": access_token,
                "refresh": refresh_token,
            }

            logger.debug(f"Login successful for user: {user.email}")
            return Response(data, status=status.HTTP_200_OK)
        else:
            logger.error(f"Login failed with data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)