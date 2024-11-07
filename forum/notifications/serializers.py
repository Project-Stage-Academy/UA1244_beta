"""
Serializers for the notifications app.

This module includes serializers for managing notifications, notification preferences for investors and startups,
and serializers for triggering notifications based on user actions.
"""

from rest_framework import serializers
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Handles serialization and deserialization of Notification objects.
    """
    class Meta:
        model = Notification
        fields = ['id', 'trigger', 'is_read', 'redirection_url', 'date_time']


class StartupNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for startup-specific notification preferences.
    Includes fields for email and push notifications.
    """
    class Meta:
        model = StartupNotificationPreferences
        fields = [
            'email_project_updates', 'push_project_updates',
            'email_startup_updates', 'push_startup_updates'
        ]


class InvestorNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for investor-specific notification preferences.
    Includes fields for email and push notifications.
    """
    class Meta:
        model = InvestorNotificationPreferences
        fields = [
            'email_project_updates', 'push_project_updates',
            'email_startup_updates', 'push_startup_updates'
        ]


class TriggerNotificationSerializer(serializers.Serializer):
    """
    Serializer for triggering notifications based on user actions.
    Includes required fields for investor_id, startup_id, project_id, and a trigger_type.
    """
    investor_id = serializers.IntegerField(required=True)
    startup_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    trigger_type = serializers.ChoiceField(
        choices=[
            ('project_follow', 'Project follow'),
            ('startup_profile_update', 'Startup profile update')
        ],
        required=True
    )
