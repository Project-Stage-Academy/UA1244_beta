"""
App configuration for the Users application.

This module defines the application configuration class for the Users app, 
setting the default primary key field type and application name.
"""

from django.apps import AppConfig

class UsersConfig(AppConfig):
    """
    Configuration class for the Users application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
