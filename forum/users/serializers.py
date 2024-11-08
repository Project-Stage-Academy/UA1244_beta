"""
Serializers for the User and Role models.

This module contains serializers that handle the serialization and deserialization
of User and Role instances, including user authentication and user data updates.
"""

from datetime import timedelta
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from .models import User, Role
from .tasks import send_activation_email


class CustomToken(AccessToken):
    """
    Custom token for user account activation.

    This token is used specifically for account activation purposes and has a 
    longer expiration time compared to the default access token.

    Attributes:
        token_type (str): Specifies the type of token (e.g., 'activation').
        lifetime (timedelta): Defines the lifespan of the token, valid for 2 days.
    """
    
    token_type = "activation"
    lifetime = timedelta(days=2)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Handles the serialization and deserialization of User instances, including
    creating a new user and assigning roles.

    Attributes:
        roles (SlugRelatedField): A field for processing roles associated with the user.
        password (CharField): A write-only field for handling the user's password.
    """
    roles = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='name',
        many=True,
        required=False
    )
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'first_name', 'last_name',
            'email', 'phone', 'roles', 'password', 'created_at',
            'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Create a new user instance with the given validated data.

        This method extracts roles from the validated data, creates a user,
        hashes the password, and assigns roles to the user if provided.

        Args:
            validated_data (dict): The validated data for creating a new user.

        Returns:
            User: The created user instance.
        """
        roles_data = validated_data.pop('roles', [])
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)

        if roles_data:
            user.roles.set(roles_data)

        token = CustomToken.for_user(user)
        activation_url = f"{settings.FRONTEND_URL}{reverse('activate', kwargs={'token': str(token)})}"
        send_activation_email.delay(user.user_id, activation_url)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates the user's email and password
    and authenticates the user if the credentials are correct.

    Fields:
        email (EmailField): The user's email, required for login.
        password (CharField): The user's password, required for login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """
        Validates the email and password credentials.

        Args:
            data (dict): Contains 'email' and 'password' keys.

        Returns:
            dict: Contains the 'user' instance if authentication is successful.

        Raises:
            AuthenticationFailed: If the email does not exist or the password is incorrect.
        """
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User with this email does not exist.") from exc

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password.")

        return {"user": user}

    def create(self, validated_data):
        """
        Placeholder for the LoginSerializer create method, not implemented.
        """
        raise NotImplementedError("LoginSerializer does not implement create method.")

    def update(self, instance, validated_data):
        """
        Placeholder for the LoginSerializer update method, not implemented.
        """
        raise NotImplementedError("LoginSerializer does not implement update method.")


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information. Provides fields for updating
    basic user details, excluding the role, which is read-only.

    Fields:
        username (CharField): The user's unique username.
        first_name (CharField): The user's first name.
        last_name (CharField): The user's last name.
        email (EmailField): The user's email address.
        phone (PhoneNumberField): The user's phone number.
        active_role (ReadOnlyField): The user's active role, read-only.
    """
    active_role = serializers.ReadOnlyField(source='active_role.name')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'phone', 'active_role'
        )
        read_only_fields = ('active_role',)
