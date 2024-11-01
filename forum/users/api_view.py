import os
from datetime import timedelta
import requests
import logging
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Role
from .serializers import UserSerializer, LoginSerializer, CustomToken
from .permissions import IsAdmin, IsOwner, IsInvestor, IsStartup
from .tasks import send_welcome_email

logger = logging.getLogger(__name__)

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
GITHUB_USER_URL = "https://api.github.com/user"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

User = get_user_model()

class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Manages user retrieval, updating, and listing operations.

    **Main Operations**:
    - **Retrieve a user**: 
        - Requires authentication. Only the owner or an admin can retrieve user details.
        - Permissions: `IsAuthenticated`, `IsOwner` or `IsAdmin`.

    - **Update a user**:
        - Requires authentication. Only the user themselves can update their information.
        - Permissions: `IsAuthenticated`, `IsOwner`.

    - **List users**:
        - Admins can view a list of all users.
        - Permissions: `IsAuthenticated`, `IsAdmin`.

    **Permissions**:
    Depending on the action (`retrieve`, `update`, `partial_update`, `list`), permissions are dynamically applied to ensure security.

    **Attributes**:
    - `queryset`: Defines the set of users that can be retrieved or updated.
    - `serializer_class`: Specifies the serializer to be used for handling user data.
    - `authentication_classes`: Uses JWTAuthentication for securing the API endpoints.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Customizes permissions for each action in the viewset.
        
        For retrieving, both owners and admins can access the resource.
        For updating, only the owner has permission.
        For listing, only admins can view all users.
        
        Returns:
            List of permission classes dynamically based on the action.
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

    **Main Operation**:
    - **Create a new user**:
        - Uses the `UserSerializer` to validate the request data and create a user.
        - After successful registration, JWT tokens (access and refresh) are returned to the user.

    **Permissions**:
    - Publicly accessible, no authentication is required.
    - Throttled using `AnonRateThrottle` to prevent abuse by unauthenticated users.

    **Attributes**:
    - `queryset`: Represents all users in the system, though mainly for creating new ones.
    - `serializer_class`: Handles user data validation and creation.
    - `throttle_classes`: Anonymously throttles requests to avoid abuse.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        """
        Handles user registration.

        Validates the input data using the `UserSerializer`, saves the new user, and generates JWT tokens.

        Returns:
            A JSON response containing the created user data and JWT tokens (access and refresh).
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

    Args:
        message (str): The error message to be returned in the response.
        status_code (int): The HTTP status code for the response.

    Returns:
        Response: A DRF `Response` object containing the error message and status code.
    """
    return Response({'error': message}, status=status_code)

class ActivateAccountView(APIView):
    """
    Handles account activation for newly registered users via a token-based system.

    **Main Operation**:
    - **Activate a user's account**:
        - The user provides a token (sent via email) which is validated to activate their account.
        - If valid, the user's account is activated, and their role is assigned if applicable.

    **Permissions**:
    - Publicly accessible, but throttled to prevent abuse.

    **Attributes**:
    - `permission_classes`: Allows public access.
    - `throttle_classes`: Limits request frequency to prevent abuse.

    **Responses**:
    - **Success**: The account is activated successfully.
    - **Failure**: Invalid or expired tokens result in an error.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request, token, *args, **kwargs):
        """
        Activates a user's account based on the provided token.

        Args:
            token (str): The activation token used to verify the user's identity.

        Returns:
            A JSON response indicating the success or failure of the activation.
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
            send_welcome_email.delay(user.user_id)

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

    **Main Operation**:
    - **Sign out**:
        - Invalidates both access and refresh tokens by setting their expiration to zero.
        - Deletes the JWT tokens from client-side cookies.

    **Permissions**:
    - Requires the user to be authenticated.
    
    **Responses**:
    - **Success**: Tokens are invalidated and removed.
    - **Failure**: Invalid tokens result in an error.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalidates the user's access and refresh tokens, effectively logging them out.

        Returns:
            A JSON response confirming the logout or an error if token invalidation fails.
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

    **Main Operation**:
    - **Change active role**: 
        - Updates the user's active role based on the provided role name.

    **Permissions**:
    - Requires the user to be authenticated.
    
    **Responses**:
    - **Success**: The active role is changed.
    - **Failure**: If the role doesn't exist or isn't provided, an error is returned.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Updates the user's active role.

        Args:
            role (str): The new role to set as the user's active role.

        Returns:
            A JSON response confirming the role change or an error if the role is invalid.
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

        Returns:
            A JSON response with a welcome message for investors.
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

        Returns:
            A JSON response with a welcome message for startups.
        """
        return Response({"message": "Welcome, Startup!"})

class LoginAPIView(APIView):
    """
    Authenticates users and provides JWT tokens for session management.

    **Main Operation**:
    - **Login**: Validates user credentials and returns access and refresh tokens.

    **Permissions**:
    - Publicly accessible (no authentication required).

    **Responses**:
    - **Success**: Returns a JWT access token and refresh token on successful login.
    - **Failure**: Returns validation errors or authentication failure messages.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Authenticates the user and returns JWT tokens.

        Returns:
            A JSON response containing access and refresh tokens if authentication is successful.
            Otherwise, returns a 400 or 401 error.
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
    API view to handle OAuth token requests by exchanging an authorization code for access and refresh tokens.
    Supports Google as the OAuth provider.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles the OAuth token request by exchanging the authorization code for an access token.
        
        Parameters:
            request (Request): The HTTP request containing provider and code in the request data.
        
        Returns:
            Response: JSON response containing access and refresh tokens if successful, 
                      or an error message if the request fails.
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
        
        Parameters:
            user_data (dict): Dictionary containing user profile information, typically including email.
        
        Returns:
            User: A User instance matching the provided data.
        
        Raises:
            ValueError: If email is not provided in the user data.
        """
        email = user_data.get('email')
        if not email:
            raise ValueError("Email not provided by OAuth provider. Please make sure your email is public.")

        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
        if created:
            user.is_active = True  
            user.save()
            logger.info(f"Created new user: {user.email}")
        else:
            logger.info(f"User found: {user.email}")
        
        return user

    def exchange_code_and_get_user_profile(self, code, provider):
        """
        Exchanges an authorization code for an access token and retrieves the user profile.
        
        Parameters:
            code (str): Authorization code received from the OAuth provider.
            provider (str): Name of the OAuth provider, currently supports 'google' only.
        
        Returns:
            tuple: Access token and user profile data.
        
        Raises:
            ValueError: If an unsupported provider is specified.
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
        
        Parameters:
            code (str): The authorization code to exchange.
            token_url (str): The URL to request the access token.
            client_id (str): Client ID for the OAuth application.
            client_secret (str): Client secret for the OAuth application.
            redirect_uri (str, optional): Redirect URI for the OAuth application.
        
        Returns:
            str: Access token provided by the OAuth provider.
        
        Raises:
            ValueError: If the access token is not present in the provider's response.
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
        
        Parameters:
            access_token (str): Access token for authentication.
            userinfo_url (str): URL to fetch user profile data.
        
        Returns:
            dict: Dictionary containing user's profile information.
        
        Raises:
            ValueError: If fetching the user profile fails.
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(userinfo_url, headers=headers)

        if response.status_code != 200:
            raise ValueError("Failed to fetch user profile from provider.")

        return response.json()
