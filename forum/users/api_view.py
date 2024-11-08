"""
api_view.py

This module defines API views for managing user-related operations including 
user registration, authentication, account activation, password reset, and 
role management. 

It leverages Django REST Framework and implements JWT authentication to secure 
endpoints. The module includes views for both public and authenticated actions.
"""

import os
import logging
from datetime import timedelta
import requests
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .models import Role
from .serializers import UserSerializer, LoginSerializer, CustomToken, UserUpdateSerializer
from .permissions import IsAdmin, IsOwner, IsInvestor, IsStartup
from .tasks import send_welcome_email, send_reset_password_email

logger = logging.getLogger(__name__)

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

User = get_user_model()

class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Manages user retrieval, updating, and listing operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Customizes permissions for each action in the viewset.
        """
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
    Handles user registration by creating new user accounts.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Handles user registration.
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

def create_error_response(message, status_code):
    """
    Generates a consistent error response format for various views.
    """
    return Response({'error': message}, status=status_code)

class ActivateAccountView(APIView):
    """
    Handles account activation for newly registered users via a token-based system.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, token, *args, **kwargs):
        """
        Activates a user's account based on the provided token.
        """
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
            send_welcome_email.apply_async(args=[user.user_id])

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
    Handles user logout by invalidating JWT tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalidates the user's access and refresh tokens, effectively logging them out.
        """
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
            return create_error_response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return create_error_response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangeActiveRoleAPIView(APIView):
    """
    Allows users to change their active role (e.g., investor, startup).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Updates the user's active role.
        """
        role_name = request.data.get('role')

        if not role_name:
            return create_error_response({"detail": "Role name is required."}, status=status.HTTP_400_BAD_REQUEST)

        role = Role.objects.filter(name=role_name).first()

        if not role:
            raise NotFound(detail=f"Role {role_name} does not exist.")

        request.user.change_active_role(role_name)

        return Response({"detail": f"Active role changed to {role_name}"}, status=status.HTTP_200_OK)

class InvestorOnlyView(APIView):
    """
    Provides content exclusively for users with the "Investor" role.
    """
    permission_classes = [IsInvestor]

    def get(self, request):
        """
        Returns a message welcoming the investor.
        """
        return Response({"message": "Welcome, Investor!"})

class StartupOnlyView(APIView):
    """
    Provides content exclusively for users with the "Startup" role.
    """
    permission_classes = [IsStartup]

    def get(self, request):
        """
        Returns a message welcoming the startup.
        """
        return Response({"message": "Welcome, Startup!"})

class LoginAPIView(APIView):
    """
    Authenticates users and provides JWT tokens for session management.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Authenticates the user and returns JWT tokens.
        """
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

            return Response(data, status=status.HTTP_200_OK)

class OAuthTokenObtainPairView(APIView):
    """
    API view to handle OAuth token requests by exchanging an authorization code 
    for access and refresh tokens.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        """
        Handles the OAuth token request by exchanging the authorization code for an access token.
        """
        provider = request.data.get('provider')
        code = request.data.get('code')

        if not provider or not code:
            return Response({"error": "Provider and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token, user_data = self.exchange_code_and_get_user_profile(code, provider)
            user = self.get_or_create_user(user_data)

            if not user.is_active:
                return Response({"error": "User account is inactive."}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_or_create_user(self, user_data):
        """
        Retrieves an existing user or creates a new one based on OAuth profile data.
        """
        email = user_data.get('email')
        if not email:
            raise ValueError("Email not provided by OAuth provider. Please make sure your email is public.")

        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
        if created:
            user.is_active = True  
            user.save()
            logger.info("Created new user: %s", user.email)
            send_welcome_email.apply_async(args=[user.user_id])
        else:
            logger.info("User found: %s", user.email)
        
        return user

    def exchange_code_and_get_user_profile(self, code, provider):
        """
        Exchanges an authorization code for an access token and retrieves the user profile.
        """
        if provider != 'google':
            raise ValueError("Unsupported provider")

        access_token = self.exchange_code_for_token(
            code,
            token_url=GOOGLE_TOKEN_URL,
            client_id=os.environ.get('GOOGLE_CLIENT_ID'),
            client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
            redirect_uri=os.environ.get('GOOGLE_REDIRECT_URI'),
        )
        user_data = self.get_user_profile(access_token, GOOGLE_USERINFO_URL)
        return access_token, user_data

    def exchange_code_for_token(self, code, token_url, client_id, client_secret, redirect_uri=None):
        """
        Exchanges the authorization code for an access token.
        """
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
        }
        if redirect_uri:
            data['redirect_uri'] = redirect_uri

        headers = {'Accept': 'application/json'}
        response = requests.post(token_url, data=data, headers=headers)
        response_data = response.json()

        if 'access_token' not in response_data:
            raise ValueError("Failed to obtain access token from provider.")
        
        return response_data['access_token']

    def get_user_profile(self, access_token, userinfo_url):
        """
        Retrieves user profile information using the access token.
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)

        if response.status_code != 200:
            raise ValueError("Failed to fetch user profile from provider.")

        return response.json()

class ResetPasswordRequestView(APIView):
    """
    View to handle requests for password reset email generation.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        """
        Handle POST request to initiate a password reset email.
        """
        email = request.data.get('email')
        logger.info("Requested email: %s", email)

        try:
            user = User.objects.get(email=email)
            logger.info("Queueing password reset email for user %s", user.email)
            send_reset_password_email.delay(user.user_id)
            logger.info("Password reset email queued for %s.", user.email)

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response("User with this email does not exist.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return create_error_response("Failed to send password reset email.", status.HTTP_500_INTERNAL_SERVER_ERROR)

def validate_password_policy(password):
    """
    Validates the password against predefined complexity requirements.
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return "Password must contain at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?`~" for char in password):
        return "Password must contain at least one special character."
    return ""

class ResetPasswordConfirmView(APIView):
    """
    View to confirm password reset using a UID and token.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, uidb64, token):
        """
        Handle POST request to reset the password for a given user.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                password = request.data.get('password')

                validation_error = validate_password_policy(password)
                if validation_error:
                    return create_error_response(validation_error, status.HTTP_400_BAD_REQUEST)

                user.set_password(password)
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return create_error_response("Invalid or expired token.", status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return create_error_response("Invalid token.", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return create_error_response("Failed to reset password.", status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserUpdateView(APIView):
    """
    API endpoint to retrieve and update user information, excluding the role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve user information.
        """
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Update user information.
        """
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return create_error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
