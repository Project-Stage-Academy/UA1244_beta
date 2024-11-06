from django.apps import AppConfig

class UsersConfig(AppConfig):
    """
    Configuration class for the Users application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    