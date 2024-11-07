"""
App configuration for the notifications application.

This configuration includes application initialization settings
and imports necessary signals when the app is ready.
"""

from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    """
    Configurations for the Notifications application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        """
        Imports signal handlers for the notifications app.
        This is necessary to ensure signal receivers are registered
        when the app is initialized.
        """
        import notifications.signals  # pylint: disable=import-outside-toplevel, unused-import

