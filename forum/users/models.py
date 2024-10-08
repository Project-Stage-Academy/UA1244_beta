from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


INVESTOR = 'investor'
STARTUP = 'startup'
    
ROLE_CHOICES = [
        (INVESTOR, 'Investor'),
        (STARTUP, 'Startup'),
    ]

class CustomUserManager(BaseUserManager):
    """
    Custom manager for User model that provides methods for creating users and superusers.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given email and password.
        
        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            **extra_fields: Additional fields for the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the email field is not provided.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with the given email and password.
        
        Args:
            email (str): The superuser's email address.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields for the superuser.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """
    Role model representing a user's role in the system.

    Attributes:
        role_id (UUIDField): Unique identifier for each role.
        role_name (CharField): The name of the role, either 'investor' or 'startup'.
    """


    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that represents users in the system.

    Attributes:
        user_id (UUIDField): Unique identifier for each user.
        user_name (CharField): Unique username for the user.
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user.
        email (EmailField): Unique email address for the user.
        password (CharField): Password for the user.
        user_phone (PhoneNumberField): Phone number of the user.
        roles (ManyToManyField): Roles assigned to the user.
        is_active (BooleanField): Indicates whether the user's account is active.
        is_staff (BooleanField): Indicates whether the user has staff privileges.
        created_at (DateTimeField): Date and time when the user account was created.
        updated_at (DateTimeField): Date and time when the user account was last updated.

    Methods:
        set_password(password): Sets the user's password.
    """

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False, max_length=255)
    password = models.CharField(max_length=255)
    phone = PhoneNumberField()
    roles = models.ManyToManyField(Role, related_name="users")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    
    def __str__(self):
        return self.email





