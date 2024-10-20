from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from .models import User, Role
from .serializers import UserSerializer, LoginSerializer
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
        else:
            return create_error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
