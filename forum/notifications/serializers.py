from rest_framework import serializers
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """
    class Meta:
        model = Notification
        fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time', 'redirection_url']

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