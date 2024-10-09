from rest_framework import serializers
from .models import User, Role
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from .tasks import send_activation_email



class CustomToken(AccessToken):
    """
    Custom token for user account activation.

    This token is used specifically for account activation purposes and has a longer expiration time 
    compared to the default access token. It inherits from the `AccessToken` class and can be 
    customized to fit specific requirements, such as changing the lifetime of the token or adding 
    custom claims.

    Attributes:
        token_type (str): Specifies the type of token (e.g., 'activation').
        lifetime (timedelta): Defines the lifespan of the token. In this case, the token is valid for 2 days.
    
    Methods:
        for_user(user):
            Generates the activation token for a specific user.
    """
    
    token_type = "activation"
    lifetime = timedelta(days=2) 



class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer handles the serialization and deserialization of User instances,
    including creating a new user and assigning roles.

    Attributes:
        roles (SlugRelatedField): A field for representing and processing roles associated with the user.
            Allows passing role names directly in the input data.
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
        """
        Meta options for UserSerializer.

        Attributes:
            model (User): The User model being serialized.
            fields (list): List of fields to include in the serialized output.
            read_only_fields (tuple): Fields that should be read-only.
            extra_kwargs (dict): Additional settings for specific fields.
        """
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email', 'phone', 'roles', 'password', 'created_at', 'updated_at']
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
    print("Creating user with data:", validated_data)  
    roles_data = validated_data.pop('roles', [])
    user = User.objects.create_user(**validated_data)
    if roles_data:
        user.roles.set(roles_data)

    token = CustomToken.for_user(user)
    activation_url = f"{settings.FRONTEND_URL}{reverse('activate', kwargs={'token': str(token)})}"
    send_activation_email.delay(user.user_id, activation_url)

    return user
