from rest_framework import serializers
from .models import User, Role
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

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
        
        roles_data = validated_data.pop('roles', [])
        user = User.objects.create_user(**validated_data)
        if roles_data:
            user.roles.set(roles_data)
            
        token = RefreshToken.for_user(user).access_token
        
        
        activation_url = f"http://localhost:8000{reverse('activate', kwargs={'token': str(token)})}"
        
        
        send_mail(
            subject='Activate Your Account',
            message=f'Hi {user.first_name},\n\nPlease click the link below to activate your account:\n{activation_url}',
            from_email=settings.EMAIL_HOST_USER,  
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user
