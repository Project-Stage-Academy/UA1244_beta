"""
models.py

This module defines custom models and managers for the users application.

Classes:
    CustomUserManager: A custom manager for handling user creation, including regular users and superusers.
    Role: A model representing a user's role in the system, such as 'startup', 'investor', or 'unassigned'.
    User: A custom user model that extends Django's AbstractBaseUser, adding fields for roles, active status, 
          and other attributes.
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

ROLE_CHOICES = [
    ('startup', 'Startup'),
    ('investor', 'Investor'),
    ('unassigned', 'Unassigned'),
]

class CustomUserManager(BaseUserManager):
    """
    Custom manager for User model that provides methods for creating users and superusers.
    """

    def create_user(self, email, password=None, active_role=None, **extra_fields):
        """
        Creates and returns a regular user with the given email and password.
        
        Args:
            email (str): The user's email address.
            password (str, optional): The user's password.
            active_role (Role, optional): The active role of the user.
            **extra_fields: Additional fields for the user.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the email field is not provided.
        """
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        if not active_role:
            active_role = Role.objects.filter(name='unassigned').first()

        user = self.model(email=email, active_role=active_role, **extra_fields)
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
        name (CharField): The name of the role, either 'investor', 'startup', or 'unassigned'.
    """
    role_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, null=False)

    objects = models.Manager()
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        """
        String representation of the Role model.

        Returns:
            str: Name of the role.
        """
        return str(self.name)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that represents users in the system.

    Attributes:
        user_id (UUIDField): Unique identifier for each user.
        username (CharField): Unique username for the user.
        first_name (CharField): First name of the user.
        last_name (CharField): Last name of the user.
        email (EmailField): Unique email address for the user.
        phone (PhoneNumberField): Phone number of the user.
        roles (ManyToManyField): Roles assigned to the user.
        active_role (ForeignKey): Active role for the user with default as 'unassigned'.
        is_active (BooleanField): Indicates whether the user's account is active.
        is_staff (BooleanField): Indicates whether the user has staff privileges.
        created_at (DateTimeField): Date and time when the user account was created.
        updated_at (DateTimeField): Date and time when the user account was last updated.

    Methods:
        change_active_role(role_name): Changes the user's active role.
    """
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    email = models.EmailField(unique=True, null=False, max_length=255)
    password = models.CharField(max_length=255)
    phone = PhoneNumberField()
    active_role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, related_name='active_users', null=True
    )
    roles = models.ManyToManyField(Role, related_name="users")
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def change_active_role(self, role_name):
        """
        Change the active role of the user to the given role name.

        Args:
            role_name (str): The name of the role to set as active.

        Raises:
            ValueError: If the role with the given name does not exist.
        """
        role = Role.objects.filter(name=role_name).first()
        if role:
            self.active_role = role
            self.save()
        else:
            raise ValueError(f"Role {role_name} does not exist.")

    def __str__(self):
        """
        String representation of the User model.

        Returns:
            str: Email of the user.
        """
        return str(self.email)
