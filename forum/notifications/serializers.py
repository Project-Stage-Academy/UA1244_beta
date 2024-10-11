from rest_framework import serializers
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'trigger', 'is_read', 'redirection_url', 'date_time']

class StartupNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for StartupNotificationPreferences model.
    """
    class Meta:
        model = StartupNotificationPreferences
        fields = ['email_project_updates', 'push_project_updates', 'email_startup_updates', 'push_startup_updates']

class InvestorNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for InvestorNotificationPreferences model.
    """
    class Meta:
        model = InvestorNotificationPreferences
        fields = ['email_project_updates', 'push_project_updates', 'email_startup_updates', 'push_startup_updates']